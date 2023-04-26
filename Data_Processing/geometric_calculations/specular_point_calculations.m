%%
% This script is for calculating height of the drone above water (Boulder Reservoir) using Specular Point geometry, satellite position, drone position, and signal travel time using code delays.

%% Load
load("/MATLAB Drive/AcquisitionData.mat")
% drone_ecef = load('drone_ecef');

%% Variables
c = 3e8; % m/s
boulder_alt = 1578; % m
f = 22e6; % Hz; sampling rate
% theta = elevation angle; custom calculation from Daniel
theta = 53; % degrees
% note: satellite ECEF may need checking
sat_ecef = [16163520.8974696, -9843045.49135850, -18726663.2253074];
drone_ecef = [-1283735.27281595, -4716511.5858851, 4086189.19958057];

%% Find max of normalized values
max_values = maxk(normalized, 1);
max_values = sort(max_values);
biggest_signal_values = max_values(end-2+1:end);
% TODO: automate finding these peak code delays

% Find rows and columns of those values (row=doppler, col=code delay)
% Code delay in [Samples]
code_delay1 = 10208; % direct
code_delay2 = 792; % samples; reflected

% Determine timing of signals
% samples/f = [seconds]

% this is relative time
% Relative time based on code delay
direct_time = code_delay1/f;
reflected_time_total = code_delay2/f;

%% Convert satellite and drone to ECEF
[sp_lat, sp_lon] = sp_calc(sat_ecef, drone_ecef, 1578, drone_ecef);

%% Convert lat/long/alt to ECEF
alt = boulder_alt;
SP_ecef = lla2ecef([sp_lat sp_lon alt]);

%% Distance between SP and satellite
SP_to_sat_distance = sqrt(sum((sat_ecef - SP_ecef).^2)); % m
SP_to_drone_distance = sqrt(sum(drone_ecef - SP_ecef).^2); % m
drone_to_sat_distance = sqrt(sum(sat_ecef - drone_ecef).^2); % m

%% Time it takes for signal to travel (based on geometry)
drone_to_sat_time = drone_to_sat_distance/c; % seconds
SP_to_sat_time = SP_to_sat_distance/c; % seconds
SP_to_drone_time = SP_to_drone_distance/c; % seconds

%% Relative time based on code delay
% Are they equal?
relative_code_delay_time = reflected_time_total - direct_time;
relative_travel_time = (SP_to_drone_time + SP_to_sat_time) - drone_to_sat_time;
fprintf('Relative Code Delay Time [s]: %f\n', relative_code_delay_time);
fprintf('Relative Signal Travel Time [s]: %f\n', relative_travel_time);

%% Height of drone
height_of_drone = sin(theta)*SP_to_drone_distance;


%*sp_height is the reflection surface height, it is okay to have some error,
% which will become an error in SP estimation of comparable magnitude.
%*x0 is a location to start the optimization search, here you can just use
% the receiver location.

%% specular point definition
% must be at end of script
function [sp_lat, sp_lon] = sp_calc(Tx_ecef, Rx_ecef, sp_height, x0)
fun = @(x)(norm(lla2ecef([x(1) x(2) sp_height])-Tx_ecef') + ...
    norm(lla2ecef([x(1) x(2) sp_height])-Rx_ecef'));
x = fminsearch(fun,x0);
sp_lat = x(1);
sp_lon = x(2);
end

