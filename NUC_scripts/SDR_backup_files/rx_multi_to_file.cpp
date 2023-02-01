#include <algorithm>
#include <complex>
#include <csignal>
#include <fstream>
#include <iostream>
#include <streambuf>
#include <string>
#include <vector>

#include <syscall.h>

#include <boost/asio.hpp>
#include <boost/bind.hpp>
#include <boost/chrono.hpp>
#include <boost/date_time.hpp>
#include <boost/filesystem.hpp>
#include <boost/format.hpp>
#include <boost/function.hpp>
#include <boost/interprocess/mapped_region.hpp>
#include <boost/interprocess/shared_memory_object.hpp>
#include <boost/interprocess/sync/interprocess_condition_any.hpp>
#include <boost/interprocess/sync/interprocess_sharable_mutex.hpp>
#include <boost/interprocess/sync/sharable_lock.hpp>
#include <boost/locale.hpp>
#include <boost/program_options.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/xml_parser.hpp>
#include <boost/ref.hpp>
#include <boost/shared_ptr.hpp>
#include <boost/signals2.hpp>
#include <boost/thread.hpp>

#include <uhd/version.hpp>
#include <uhd/types/tune_request.hpp>
#if UHD_VERSION < 3110000
#include <uhd/utils/thread_priority.hpp>
#else
#include <uhd/utils/thread.hpp>
#endif
#include <uhd/exception.hpp>
#include <uhd/types/tune_request.hpp>
#include <uhd/utils/safe_main.hpp>
#include <uhd/usrp/multi_usrp.hpp>

#include "buffered_fstream.hpp"
#include "cbuff_handler.hpp"
#include "io_runner.hpp"
#include "mu_meta.hpp"

#define BUFFER_BYTES 268435456

namespace asio = boost::asio;
namespace fs = boost::filesystem;
namespace ipc = boost::interprocess;
namespace po = boost::program_options;
namespace pt = boost::property_tree;
namespace ptm = boost::posix_time;
namespace si = boost::signals2;

class usrp_multi_args {
public:
  std::string args;
  double sample_rate;
  std::string wirefmt;
  std::string osc_source;
  std::string time_source;
  size_t buffer_time;
  unsigned long min_free;
  bool write_meta;
  std::string peak;
  std::string type;
  std::string extension;
  size_t ch_offset;
  std::vector<double> center_freq;
  std::vector<std::string> subdev;
  std::vector<std::string> lo_src;
  std::vector<bool> lo_export;
  std::vector<double> gain;
  std::vector<double> bandwidth;
  std::vector<std::string> antenna;
  std::vector<std::string> path_name;
  std::vector<std::string> path_name2;
  std::vector<std::string> site_id;
};

class settings {
public: 
  void load(const std::string& filename) {
    pt::ptree tree;
    pt::xml_parser::read_xml(filename, tree);
    pt::ptree usrp_multi_nodes = tree.get_child("uhd");
    for(auto usrp_multi: usrp_multi_nodes) {
      if(not std::strncmp(usrp_multi.first.data(), "usrp_multi", 10)) {
	usrp_multi_args args;
	args.args = usrp_multi.second.get<std::string>("args");
	args.sample_rate = usrp_multi.second.get<double>("sample_rate");
	args.wirefmt = usrp_multi.second.get<std::string>("wirefmt");
	args.osc_source = usrp_multi.second.get<std::string>("osc_source");
	args.time_source = usrp_multi.second.get<std::string>("time_source");
	args.buffer_time = usrp_multi.second.get<size_t>("buffer_time");
	args.min_free = usrp_multi.second.get<unsigned long>("min_free");
	args.write_meta = usrp_multi.second.get<bool>("write_meta");
	args.peak = usrp_multi.second.get<std::string>("peak");
	args.type = usrp_multi.second.get<std::string>("type");
	args.extension = usrp_multi.second.get<std::string>("extension");
	args.ch_offset = usrp_multi.second.get<size_t>("channel_offset");
	pt::ptree stream_nodes = usrp_multi.second.get_child("");
	for(auto stream : stream_nodes) {
	  if(not std::strncmp(stream.first.data(), "stream", 6)) {
	    args.center_freq.push_back(stream.second.get<double>("center_freq"));
	    args.subdev.push_back(stream.second.get<std::string>("subdev"));
	    args.lo_src.push_back(stream.second.get<std::string>("lo", ""));
	    args.lo_export.push_back(stream.second.get<bool>("export", false));
	    args.gain.push_back(stream.second.get<double>("gain"));
	    args.bandwidth.push_back(stream.second.get<double>("bandwidth"));
	    args.antenna.push_back(stream.second.get<std::string>("antenna"));
	    args.path_name.push_back(stream.second.get<std::string>("path_name"));
	    args.path_name2.push_back(stream.second.get<std::string>("path_name2"));
	    args.site_id.push_back(stream.second.get<std::string>("site_id"));
	  }
	}
	settings.push_back(args);
      }
    }
  }

  void print(void) {
    for(auto a : settings) {
      std::cout << "args: " << a.args << std::endl;
      for(auto b : a.center_freq) 
	std::cout << "Center Freq: " << b << std::endl;
      for(auto b : a.type) 
	std::cout << "Type: " << b << std::endl;
    }
  }
	

  std::vector<usrp_multi_args> settings;

};

class uhd_cbuffer_multi {
public:
  uhd_cbuffer_multi(usrp_multi_args& args, bool has_pps = false) :
    _sample_rate_hz(args.sample_rate), 
    _wirefmt(args.wirefmt),
    _center_freq_hz(args.center_freq),
    _path_name(args.path_name),
    _path_name2(args.path_name2),
    _site_id(args.site_id),
    _extension(args.extension),
    _type(args.type),
    _buffer_size(args.buffer_time * args.sample_rate),
    _min_free_bytes(args.min_free),
    _write_meta(args.write_meta),
    _peak(args.peak),
    _stop_signal_received(false),
    _triggered(false),
    _trigger_state_changed(false),
    _ctr(0)
  {
    for(size_t i = 0; i < _path_name2.size(); ++i) {
      if(_path_name2[i].length())
	_has_path2.push_back(true);
      else
	_has_path2.push_back(false);
    }
    
    std::for_each(_path_name.begin(), _path_name.end(), [](std::string& p) {
	if(not fs::exists(p)) {
	  std::cout << "Creating: " << p << std::endl;
	  fs::create_directories(p);
	} else {
	  if(not fs::is_directory(p)) {
	    std::cerr << "WARNING: " << p << " exists, but is not a directory." << std::endl;
	  }
	}

	if(p.back() != '/') {
	  p.push_back('/');
	}
      } );

    if(_has_path2[0]) {
      std::for_each(_path_name2.begin(), _path_name2.end(), [](std::string& p) {
	  if(not fs::exists(p)) {
	    std::cout << "Creating: " << p << std::endl;
	    fs::create_directories(p);
	  } else {
	    if(not fs::is_directory(p)) {
	      std::cerr << "WARNING: " << p << " exists, but is not a directory." << std::endl;
	    }
	  }

	  if(p.back() != '/') {
	    p.push_back('/');
	  }
	} );
    }
    
    _usrp = uhd::usrp::multi_usrp::make(uhd::device_addr_t(args.args));
    _usrp->set_clock_source(args.osc_source);
    if(has_pps) {
      _usrp->set_time_source(args.time_source);
    }
    _usrp->set_rx_rate(_sample_rate_hz);
    for(size_t i = 0; i < _center_freq_hz.size(); ++i) {
      if(args.subdev[i].length()) {
	_usrp->set_rx_subdev_spec(uhd::usrp::subdev_spec_t(args.subdev[i]), i);
      }
      uhd::tune_request_t req(_center_freq_hz[i]);
      _usrp->set_rx_freq(req, i);
      std::cout << "Asking for center frequency: " << _center_freq_hz[i] << std::endl;
      
#if UHD_VERSION >= 3100000
      if(args.lo_src[i].length()) {
	_usrp->set_rx_lo_source(args.lo_src[i], uhd::usrp::multi_usrp::ALL_LOS, i);
	_usrp->set_rx_lo_export_enabled(args.lo_export[i], uhd::usrp::multi_usrp::ALL_LOS, i);
      }
#endif
      
      _usrp->set_rx_antenna(args.antenna[i], i);
      _usrp->set_rx_gain(args.gain[i], i);
      _usrp->set_rx_bandwidth(args.bandwidth[i], i);
    }
    for(size_t i = 0; i < _center_freq_hz.size(); ++i)
      std::cout << "Actually got: " << _usrp->get_rx_freq(i) << std::endl;
    if(has_pps) {
      _usrp->set_time_next_pps(uhd::time_spec_t(0.0));
    } else {
      _usrp->set_time_now(uhd::time_spec_t(0.0));
    }

    
  }
  
  uhd_cbuffer_multi(uhd_cbuffer_multi& other) :
    _usrp(other._usrp),
    _sample_rate_hz(other._sample_rate_hz),
    _wirefmt(other._wirefmt),
    _center_freq_hz(other._center_freq_hz),
    _path_name(other._path_name),
    _path_name2(other._path_name2),
    _has_path2(other._has_path2),
    _site_id(other._site_id),
    _extension(other._extension),
    _type(other._type),
    _buffer_size(other._buffer_size),
    _min_free_bytes(other._min_free_bytes),
    _write_meta(other._write_meta),
    _peak(other._peak),
    _stop_signal_received(other._stop_signal_received),
    _triggered(other._triggered),
    _trigger_state_changed(other._trigger_state_changed),
    _ctr(other._ctr)
  { }
  uhd_cbuffer_multi(const uhd_cbuffer_multi& other) :
    _usrp(other._usrp),
    _sample_rate_hz(other._sample_rate_hz),
    _wirefmt(other._wirefmt),
    _center_freq_hz(other._center_freq_hz),
    _path_name(other._path_name),
    _path_name2(other._path_name2),
    _has_path2(other._has_path2),
    _site_id(other._site_id),
    _extension(other._extension),
    _type(other._type),
    _buffer_size(other._buffer_size),
    _min_free_bytes(other._min_free_bytes),
    _write_meta(other._write_meta),
    _peak(other._peak),
    _stop_signal_received(other._stop_signal_received),
    _triggered(other._triggered),
    _trigger_state_changed(other._trigger_state_changed),
    _ctr(other._ctr)
  { }
  uhd_cbuffer_multi(uhd_cbuffer_multi&& other) :
    _usrp(other._usrp),
    _sample_rate_hz(other._sample_rate_hz),
    _wirefmt(other._wirefmt), 
    _center_freq_hz(other._center_freq_hz),
    _path_name(other._path_name),
    _path_name2(other._path_name2),
    _has_path2(other._has_path2),
    _site_id(other._site_id),
    _extension(other._extension),
    _type(other._type),
    _buffer_size(other._buffer_size),
    _min_free_bytes(other._min_free_bytes),
    _write_meta(other._write_meta),
    _peak(other._peak),
    _stop_signal_received(other._stop_signal_received),
    _triggered(other._triggered),
    _trigger_state_changed(other._trigger_state_changed),
    _ctr(other._ctr)
  { }

  uhd_cbuffer_multi& operator=(const uhd_cbuffer_multi& other) {
    _usrp = other._usrp;
    _sample_rate_hz = other._sample_rate_hz;
    _wirefmt = other._wirefmt;
    _center_freq_hz = other._center_freq_hz;
    _path_name = other._path_name;
    _path_name2 = other._path_name2;
    _has_path2 = other._has_path2;
    _site_id = other._site_id;
    _extension = other._extension;
    _type = other._type;
    _buffer_size = other._buffer_size;
    _min_free_bytes = other._min_free_bytes;
    _write_meta = other._write_meta;
    _peak = other._peak;
    _stop_signal_received = other._stop_signal_received;
    _triggered = other._triggered;
    _trigger_state_changed = other._trigger_state_changed;
    _ctr = other._ctr;
    return *this;
  }

  void set_time_next_pps(const uhd::time_spec_t time_spec) {
    _usrp->set_time_next_pps(time_spec);
  }

  double get_time_now(void) {
    return _usrp->get_time_now().get_real_secs();
  }

  bool check_sensors_locked(size_t num_usrps) {
    bool ret = true;
    std::vector<std::string> sensors;
    for(size_t i = 0; i < num_usrps; i++) {
      sensors = _usrp->get_rx_sensor_names(i);
      if(std::find(sensors.begin(), sensors.end(), "lo_locked") != sensors.end()) {
	uhd::sensor_value_t lo_locked = _usrp->get_rx_sensor("lo_locked", i);
	std::cout << boost::format("Checking RX %d: %s ...") % i % lo_locked.to_pp_string() << std::endl;
	ret = ret && lo_locked.to_bool();
      }
    }
    
    sensors = _usrp->get_mboard_sensor_names(0);
    // Skip this check if clock_source is internal
    if(_usrp->get_clock_source(0).compare("internal")) {
      uhd::sensor_value_t ref_locked = _usrp->get_mboard_sensor("ref_locked", 0);
      std::cout << boost::format("Checking MB: %s ...") % ref_locked.to_pp_string() << std::endl;
      ret = ret && ref_locked.to_bool();
    }

    return ret;
  }

  void stop(void) {
    _stop_signal_received = true;
  }

  void trigger(bool state) {
    std::cout << state << std::endl;
    if(state ^ _triggered) {
      boost::mutex::scoped_lock lock(trigger_mutex);
      _trigger_state_changed = true;
      _triggered = state;
    }
  }

  std::string make_name(size_t num, unsigned duration) {
    if(not _site_id[num].compare("null")) {
      return "null";
    }
    std::ostringstream ret;
    boost::locale::date_time now;
    ret.imbue(std::locale());
    ret << boost::locale::as::ftime("%Y%m%d_%H%M%S_") << now;
    unsigned dur_hrs = duration / 3600;
    unsigned dur_mins = (duration - dur_hrs * 3600) / 60;
    unsigned dur_secs = duration - dur_hrs * 3600 - dur_mins * 60;
    ret << boost::format("%02d%02d%02d_") % dur_hrs % dur_mins % dur_secs;
    ret << _site_id[num];
    ret << "." << _extension;
    return ret.str();
  }

  std::string make_name(size_t num, unsigned duration, ptm::ptime time) {
    if(not _site_id[num].compare("null")) {
      return "null";
    }
    std::ostringstream ret;
    std::locale loc(std::cout.getloc(), new ptm::time_facet("%Y%m%d_%H%M%S"));
    ret.imbue(loc);
    ret << (time + ptm::seconds(1));
    unsigned dur_hrs = duration / 3600;
    unsigned dur_mins = (duration - dur_hrs * 3600) / 60;
    unsigned dur_secs = duration - dur_hrs * 3600 - dur_mins * 60;
    ret << boost::format("_%02d%02d%02d_") % dur_hrs % dur_mins % dur_secs;
    ret << _site_id[num];
    ret << "." << _extension;
    return ret.str();
  }

  template<typename type>
  void thread_main(void) {
    size_t num_channels = _center_freq_hz.size();
    
    uhd::stream_args_t stream_args(_type, _wirefmt);
    stream_args.args["peak"] = _peak;
    std::vector<size_t> channels(num_channels);

    std::vector<std::vector<type> > buffs(num_channels, std::vector<type>(_sample_rate_hz / 1000));
    std::vector<type*> buff_ptrs;

    std::vector<std::string> names, names2;
    std::vector<buffered_ofstream*> ofs(num_channels), ofs2(num_channels);
    std::vector<std::ofstream> mfs(num_channels), mfs2(num_channels);
    std::vector<char*> ofs_bufs(num_channels);
    for(size_t i = 0; i < num_channels; i++) {
      names.push_back(_path_name[i] + make_name(i, 0));
      ofs[i] = new buffered_ofstream();
      ofs[i]->resize(28);
      ofs[i]->open(names[i]);
      ofs_bufs[i] = reinterpret_cast<char*>(std::malloc(BUFFER_BYTES));
      //ofs[i].rdbuf()->pubsetbuf(ofs_bufs[i], BUFFER_BYTES);
      //ofs[i].rdbuf()->pubsetbuf(0, 0);
      if(_site_id[i].compare("null")) {
	mfs[i].open(names[i] + ".usrp");
      }
    }

    for(size_t i = 0; i < num_channels; i++) {
      if(_has_path2[i]) {
	names2.push_back(_path_name2[i] + make_name(i, 0));
	ofs2[i] = new buffered_ofstream();
	ofs2[i]->resize(28);
	ofs2[i]->open(names2[i]);
	mfs2[i].open(names2[i] + ".usrp");
      }
    }
    //std::vector<boost::shared_ptr<muohio::cbuff_handler<type> > > cbh;
    
    for(size_t i = 0; i < num_channels; ++i) {
      channels[i] = i;
      buff_ptrs.push_back(&buffs[i].front());
      //cbh.push_back(boost::shared_ptr<muohio::cbuff_handler<type> >(new muohio::cbuff_handler<type>(_buffer_size, _sample_rate_hz / 1000, _path_name[i], _write_meta)));
    }
    stream_args.channels = channels;
    uhd::rx_streamer::sptr stream = _usrp->get_rx_stream(stream_args);

    std::cout << "Created RX streamer..." << std::endl;
    std::cout << buffs.size() << " " << buffs[0].size() << std::endl;

    uhd::stream_cmd_t cmd(uhd::stream_cmd_t::STREAM_MODE_START_CONTINUOUS);
    cmd.stream_now = false;
    cmd.time_spec = uhd::time_spec_t(_usrp->get_time_now().get_real_secs() + 0.1);
    stream->issue_stream_cmd(cmd);


    uhd::rx_metadata_t md;

    std::cout << "Stream command sent, waiting for USRP to settle..." << std::endl;

    for(int i = 0; i < 1000; ++i) {
      stream->recv(buff_ptrs, _sample_rate_hz / 1000, md, 0.1, false);
    }

    std::cout << "Streaming data..." << std::endl;

    ptm::ptime recording_start_ptime;

    while(not _stop_signal_received) {
      size_t num_received = stream->recv(buff_ptrs, _sample_rate_hz / 1000, md, 0.1, false);
      _ctr++;
      if(num_received != (_sample_rate_hz / 1000)) {
	//std::cout << "Wrong number of bytes received" << std::endl;
      }
      
      boost::mutex::scoped_lock lock(trigger_mutex);
      for(size_t i = 0; i < num_channels; ++i) {
	if(_triggered) {
          if(_trigger_state_changed) {
            recording_start_ptime = ptm::second_clock::universal_time();
          }
	  if(_write_meta and _site_id[i].compare("null")) {
            boost::chrono::high_resolution_clock::time_point pc_tp = boost::chrono::high_resolution_clock::now();
	    boost::chrono::high_resolution_clock::duration pc_dur = pc_tp.time_since_epoch();
	    double pc = double(pc_dur.count()) * boost::chrono::high_resolution_clock::period::num / double(boost::chrono::high_resolution_clock::period::den);
            muohio::mu_meta_t meta = muohio::mu_meta::get_meta(_ctr, md.time_spec.get_real_secs(), pc, int8_t(md.error_code));
	    if(_site_id[i].compare("null")) {
	      muohio::mu_meta::write(&mfs[i], meta);
	    }
	    if(_has_path2[i]) {
	      muohio::mu_meta::write(&mfs2[i], meta);
	    }
          }
	  ofs[i]->write(reinterpret_cast<char*>(&buffs[i].front()), sizeof(type) * _sample_rate_hz / 1000);
	  if(_has_path2[i]) {
	    ofs2[i]->write(reinterpret_cast<char*>(&buffs[i].front()), sizeof(type) * _sample_rate_hz / 1000);
	  }
	  //ofs[i].flush();
	} else {
	  if(_trigger_state_changed) {
	    ptm::ptime recording_end_ptime(ptm::second_clock::universal_time());
    
	    ofs[i]->close();
	    if(_write_meta and _site_id[i].compare("null"))
	      mfs[i].close();
	    std::string name = _path_name[i] + make_name(i, (recording_end_ptime - recording_start_ptime).total_seconds(), recording_start_ptime);
	    std::cout << "Renaming: " << names[i] << std::endl << "  to: " << name << std::endl;
	    fs::rename(names[i], name);
	    if(_write_meta and _site_id[i].compare("null"))
	      fs::rename(names[i] + ".usrp", name + ".usrp");
	    else
	      fs::remove(names[i] + ".usrp");
	    
	    names[i] = _path_name[i] + make_name(i, 0);
	    ofs[i]->open(names[i]);
	    if(_site_id[i].compare("null")) {
	      mfs[i].open(names[i] + ".usrp");
	    }

	    if(_has_path2[i]) {
	      ofs2[i]->close();
	      if(_write_meta)
		mfs2[i].close();
	      std::string name = _path_name2[i] + make_name(i, (recording_end_ptime - recording_start_ptime).total_seconds(), recording_start_ptime);
	      std::cout << "Renaming: " << names2[i] << std::endl << "  to: " << name << std::endl;
	      fs::rename(names2[i], name);
	      if(_write_meta)
		fs::rename(names2[i] + ".usrp", name + ".usrp");
	      else
		fs::remove(names2[i] + ".usrp");
	      
	      names2[i] = _path_name2[i] + make_name(i, 0);
	      ofs2[i]->open(names2[i]);
	      mfs2[i].open(names2[i] + ".usrp");
	    }
	  }
	}
	/*cbh[i]->push_array(&buffs[i]);
	  if(_triggered and _trigger_state_changed) {
	  cbh[i]->send_trigger_start();
	  //_trigger_state_changed = false;
	  }

	  if(not _triggered and _trigger_state_changed) {
	  cbh[i]->send_trigger_stop(make_name(i, num_packets / 1000));
	  num_packets = 0;
	  //_trigger_state_changed = false;
	  }*/
      }
      _trigger_state_changed = false;
      
    }
    
    std::cout << "Stop signal received, shutting down..." << std::endl;
    for(size_t i = 0; i < num_channels; ++i) {
      ofs[i]->close();
      free(ofs_bufs[i]);
      if(_site_id[i].compare("null")) {
	mfs[i].close();
	fs::remove(names[i]);
	fs::remove(names[i] + ".usrp");
      }
    }

    for(size_t i = 0; i < num_channels; ++i) {
      if(_has_path2[i]) {
	ofs2[i]->close();
	mfs2[i].close();
	fs::remove(names2[i]);
	fs::remove(names2[i] + ".usrp");
      }
    }
    
    cmd.stream_mode = uhd::stream_cmd_t::STREAM_MODE_STOP_CONTINUOUS;
    stream->issue_stream_cmd(cmd);
    
  }

private:
  uhd::usrp::multi_usrp::sptr _usrp;
  double _sample_rate_hz;
  std::string _wirefmt;
  std::vector<double> _center_freq_hz;
  std::vector<std::string> _path_name;
  std::vector<std::string> _path_name2;
  std::vector<bool> _has_path2;
  std::vector<std::string> _site_id;
  std::string _extension;
  std::string _type;
  size_t _buffer_size;
  unsigned long _min_free_bytes;
  bool _write_meta;
  std::string _peak;
  bool _stop_signal_received;
  bool _triggered, _trigger_state_changed;
  uint32_t _ctr;
  boost::mutex trigger_mutex;
};

struct shm_mtx {
  ipc::interprocess_sharable_mutex mutex;
  ipc::interprocess_condition_any cond;
  bool start_stop;
};

int UHD_SAFE_MAIN(int argc, char *argv[]) {

  std::string settings_filename, start_time, trigger_topic, app_name;

  unsigned timeout;

  bool shm_trig = false;
  
  po::options_description desc("Allowed options.");
  desc.add_options()
    ("help", "Display usage information.")
    ("settings", po::value<std::string>(&settings_filename), "Name of the xml file which holds the RF frontend tuning information.")
    ("time", po::value<unsigned>(&timeout)->default_value(1), "Time, in seconds, of the recording run (does not account for the buffer time).")
    ("start", po::value<std::string>(&start_time)->default_value("now"), "Time in \"yyyy mm dd HH MM SS\" to start recording.")
    ("shm", "Use the shared-memory trigger mechanism.")
    ;
  po::variables_map vm;
  po::store(po::parse_command_line(argc, argv, desc), vm);
  po::notify(vm);

  if(vm.count("help") or argc == 1) {
    std::cout << "CSU UHD extensions recorder with circular buffer." << desc << std::endl;
    return ~0;
  }

  if(vm.count("shm")) {
    std::cout << "Using SHM trigger, ignoring timed events." << std::endl;
    shm_trig = true;
  }

  boost::locale::generator gen;
  std::locale::global(gen(""));

  bool timed_start = false;
  ptm::ptime start_ptime;
  if(start_time.compare("now")) {
    std::locale time_format(std::locale::classic(),new ptm::time_input_facet("%Y %m %d %H %M %S"));
    std::istringstream is(start_time);
    is.imbue(time_format);
    is >> start_ptime;
    std::cout << "Read start time: " << start_ptime << std::endl;
    timed_start = true;
  }

  settings s;
  s.load(settings_filename);
  //s.print();

  std::cout << "Settings file loaded, preparing USRP devices..." << std::endl;

  std::vector<uhd_cbuffer_multi> uhd_instances;

  for(size_t i = 0; i < s.settings.size(); ++i) {
    uhd_instances.push_back(uhd_cbuffer_multi(s.settings[i], s.settings[i].time_source.length()));
  }

  for(size_t i = 0; i < s.settings.size(); ++i) {
    uhd::time_spec_t spec(0.0);
    uhd_instances[i].set_time_next_pps(spec);
  }

  std::cout << "Waiting 2 seconds for USRP's to become ready..." << std::endl;
  boost::this_thread::sleep_for(boost::chrono::seconds(2));

  std::cout << "Polling USRP's to make sure all sensors locked..." << std::endl;

  for(size_t i = 0; i < s.settings.size(); ++i) {
    double time = uhd_instances[i].get_time_now();
    std::cout << "USRP " << i << " returned time: " << time << "." << std::endl;
    if(not uhd_instances[i].check_sensors_locked(s.settings[i].gain.size())) {
      std::cout << "There was a problem starting up the USRP's." << std::endl;
      return ~0;
    }
  }

  std::vector<boost::thread> threads;

  si::signal<void ()> stop;
  si::signal<void (bool)> trigger;

  std::cout << "Starting " << s.settings.size() << " threads..." << std::endl;

  for(size_t i = 0; i < s.settings.size(); ++i) {
    if(s.settings[i].type.find("sc4") != std::string::npos)
      threads.push_back(boost::thread(boost::bind(&uhd_cbuffer_multi::thread_main<int8_t>, &uhd_instances[i])));
    else if(s.settings[i].type.find("sc8") != std::string::npos)
      threads.push_back(boost::thread(boost::bind(&uhd_cbuffer_multi::thread_main<std::complex<int8_t> >, &uhd_instances[i])));
    else if(s.settings[i].type == "sc16")
      threads.push_back(boost::thread(boost::bind(&uhd_cbuffer_multi::thread_main<std::complex<int16_t> >, &uhd_instances[i])));
    stop.connect(boost::bind(&uhd_cbuffer_multi::stop, &uhd_instances[i]));
    trigger.connect(boost::bind(&uhd_cbuffer_multi::trigger, &uhd_instances[i], boost::arg<1>()));
  }

  bool running = true;
  boost::function<void (const boost::system::error_code&, int signal_number)> signal_handler;
  signal_handler = [&stop, &trigger, &running] (const boost::system::error_code&, int signal_number) {
    if(signal_number == SIGINT) {
      trigger(false);
      running = false;
      ipc::shared_memory_object shm(ipc::open_or_create, "event_trigger", ipc::read_write);
      shm.truncate(1024);
      ipc::mapped_region region(shm, ipc::read_write);
      void* addr = region.get_address();
      shm_mtx* stop_mutex = new (addr) shm_mtx;
      stop_mutex->start_stop = false;
      {
	ipc::sharable_lock<ipc::interprocess_sharable_mutex> lock(stop_mutex->mutex);
	stop_mutex->cond.notify_all();
	stop_mutex->cond.notify_all();
      }
      boost::this_thread::sleep_for(boost::chrono::seconds(5));
      stop();
      boost::this_thread::sleep_for(boost::chrono::seconds(5));
      std::cout << "Failed to shut down cleanly, terminating." << std::endl;
      exit(0);
    }
  };

  asio::io_service io;
  asio::signal_set signals(io);
  signals.add(SIGINT);
  asio::io_service::work work(io);
  io_runner runner(io);

  signals.async_wait(boost::bind(signal_handler, asio::placeholders::error, asio::placeholders::signal_number));

  boost::this_thread::sleep_for(boost::chrono::seconds(5));
  if(not shm_trig and timed_start) {
    std::cout << "Waiting " << (start_ptime - ptm::microsec_clock::universal_time()) << " before recording." << std::endl;
    boost::this_thread::sleep_for(boost::chrono::microseconds((start_ptime - ptm::microsec_clock::universal_time()).total_microseconds()));
  }
  if(not shm_trig) {
    trigger(true);
  
    boost::this_thread::sleep_for(boost::chrono::seconds(timeout));
  
    trigger(false);
    boost::this_thread::sleep_for(boost::chrono::seconds(5));
  } else {
    while(running) {
      try {
	ipc::shared_memory_object shm(ipc::open_only, "event_trigger", ipc::read_write);
	ipc::mapped_region region(shm, ipc::read_write);
	void* addr = region.get_address();
	shm_mtx* trigger_mutex = new (addr) shm_mtx;
	ipc::sharable_lock<ipc::interprocess_sharable_mutex> lock(trigger_mutex->mutex);
	trigger_mutex->cond.wait(lock);
	trigger(trigger_mutex->start_stop);
	if(not running) break;
      } catch (ipc::interprocess_exception& e) {
	std::cout << "Problem connecting to SHM..." << e.what() << std::endl;
	boost::this_thread::sleep_for(boost::chrono::seconds(10));
      }
    }
  }

  stop();
  std::cout << "Shutdown event received..." << std::endl;

  boost::this_thread::sleep_for(boost::chrono::seconds(10));

  return 0;
}
