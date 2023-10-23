% Define the parameters of the Gaussian beam profile
w0 = 1.0; % waist radius in meters
zR = 1.0; % Rayleigh range in meters

% Define the range of interest for the beam profile
z = linspace(-2*zR, 2*zR, 1000); % 1D grid of points in the z-direction

% Evaluate the beam profile at each point in the grid
w = w0 * sqrt(1 + (z/zR).^2);
I = exp(-0.5 * (z/zR).^2) ./ (w0 * pi * w.^2);

% Visualize the beam profile
figure;
plot(z, I);
xlabel('z (m)');
ylabel('Intensity (W/m^2)');
title('Laser Beam Profile');
% Parameters of the telescope
aperture_diameter = 0.1; % meters
focal_length = 10; % meters
mirror_diameter = 0.01; % meters

% Calculate the beam divergence angle and the beam waist diameter
waist_diameter = 1.22 * aperture_diameter; % meters
waist_radius = waist_diameter / 2; % meters
divergence_angle = atan(waist_radius / focal_length); % radians

% Determine the position of the laser beam on the focal plane of the telescope
focal_plane_position = 0; % meters

% Calculate the position of the laser beam on the focal plane of the star guide
star_guide_focal_plane_position = focal_plane_position + mirror_diameter / 2 * sin(divergence_angle); % meters

% Calculate the position of the laser beam on the focal plane of the telescope after reflection from the star guide mirror
final_focal_plane_position = focal_plane_position + 2 * mirror_diameter / 2 * sin(divergence_angle); % meters

% Plot the results
figure;
plot([0, star_guide_focal_plane_position, final_focal_plane_position], 'LineWidth', 2);
xlabel('Position on the Focal Plane (m)');
ylabel('Laser Beam Position (m)');
title('Laser Beam Position on the Focal Plane of the Telescope');
legend('Initial Position', 'After Star Guide Mirror', 'Location', 'SouthEast');
grid on;