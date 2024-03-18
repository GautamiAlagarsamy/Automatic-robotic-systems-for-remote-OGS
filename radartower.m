scenario = radarScenario;
tower = platform(scenario);
tower.ClassID = 3;
%tower.Signatures{1};
load('RCSCylinderExampleData.mat','cylinder');

tower.Signatures{1} = rcsSignature('Pattern', cylinder.RCSdBsm, ...
    'Azimuth', cylinder.Azimuth, 'Elevation', cylinder.Elevation, ...
    'Frequency', cylinder.Frequency);
tower.Dimensions = struct( ...
    'Length', 10, ...
    'Width', 10, ...
    'Height', 60, ...
    'OriginOffset', [0 0 30]);
scenario.platformPoses
tower.Trajectory
tYaw = 0;
tPitch = 4;
tRoll = 0;
tower.Trajectory.Orientation = quaternion([tYaw tPitch tRoll],'eulerd','zyx','frame');
tPlot = theaterPlot('XLim',[-50 50],'YLim',[-50 50],'ZLim',[-100 0]);
pPlotter = platformPlotter(tPlot,'DisplayName','tower');

pose = platformPoses(scenario);
towerPose = pose(1);
towerDims = tower.Dimensions;

plotPlatform(pPlotter, towerPose.Position, towerDims, towerPose.Orientation);
set(tPlot.Parent,'YDir','reverse', 'ZDir','reverse');
view(tPlot.Parent, -37.5, 30)
towerRadar = radarDataGenerator('SensorIndex', 1, ...
    'UpdateRate', 10, ...
    'MountingLocation', [0 0 -60], ...
    'ScanMode', 'No scanning', ...
    'HasINS', true, ...
    'TargetReportFormat', 'Detections', ...
    'DetectionCoordinates', 'Scenario');

tower.Sensors = towerRadar;
tPlot.XLimits = [-5000 5000];
tPlot.YLimits = [-5000 5000];
tPlot.ZLimits = [-1000 0];

covPlotter = coveragePlotter(tPlot,'DisplayName','Sensor Coverage');
plotCoverage(covPlotter, coverageConfig(scenario));
helicopter = platform(scenario);
helicopter.Dimensions = struct( ...
    'Length',30, ...
    'Width', .1, ...
    'Height', 7, ...
    'OriginOffset',[0 8 -3.2]);

helicopter.Signatures = rcsSignature( ...
    'Pattern',[40 40; 40 40], ...
    'Elevation',[-90; 90], ...
    'Azimuth',[-180,180]);
    



%Platform Motion and Animation
helicopter.Trajectory = waypointTrajectory([2000 500 -250; 2000 -500 -250],[0 25]);
profiles = platformProfiles(scenario);
dimensions = vertcat(profiles.Dimensions);

while advance(scenario)
    poses = platformPoses(scenario);
    positions = vertcat(poses.Position);
    orientations = vertcat(poses.Orientation);
    plotPlatform(pPlotter, positions, dimensions, orientations);
    plotCoverage(covPlotter, coverageConfig(scenario));
    % to animate more slowly uncomment the following line
    %pause(0.01)
    % Print the position and orientation of the helicopter 
    fprintf('Helicopter Position: [%f, %f, %f]\n', helicopter.Position(1), helicopter.Position(2), helicopter.Position(3)); 
    
end



scenario.UpdateRate = 0;
fig = ancestor(tPlot.Parent,'Figure');
timeReadout = uicontrol(fig,'Style','text','HorizontalAlignment','left','Position',[0 0 200 20]);
timeReadout.String = "SimulationTime: " + scenario.SimulationTime;
dPlotter = detectionPlotter(tPlot,'DisplayName','detections');


restart(scenario);

while advance(scenario)
    timeReadout.String = "SimulationTime: " + scenario.SimulationTime;
    detections = detect(scenario);
    
    % extract column vector of measurement positions
    allDetections = [detections{:}];
    if ~isempty(allDetections)
        measurement = cat(2,allDetections.Measurement)';
            
        fprintf('Detection Position: [%f, %f, %f]\n', allDetections.Measurement(:));
               
        % call Python script with laser interaction
        system(['python plot_detection.py ' num2str(measurement)]);
    else
        measurement = zeros(0,3);
        fprintf('No detections\n');
        system(['python plot_detection.py ' num2str(measurement)]);

    end
    % Plot the detections
    plotDetection(dPlotter, measurement);
    % Plot the platforms and coverage
    poses = platformPoses(scenario);
    positions = vertcat(poses.Position);
    orientations = vertcat(poses.Orientation);
    plotPlatform(pPlotter, positions, dimensions, orientations);
    plotCoverage(covPlotter, coverageConfig(scenario));
      
end
