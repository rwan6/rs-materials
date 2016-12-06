%iterate over everything in folder and turn it into data

clc;    % Clear the command window.
workspace;  % Make sure the workspace panel is showing.
format longg;
format compact;

% Define a starting folder.
start_path = fullfile(matlabroot, '');
% Ask user to confirm or change.
topLevelFolder = uigetdir('');
if topLevelFolder == 0
	return;
end
% topLevelOutput = uigetdir(topLevelFolder);
% if topLevelOutput == 0
% 	return;
% end
% Get list of all subfolders.
allSubFolders = genpath(topLevelFolder);
% Parse into a cell array.
remain = allSubFolders;
listOfFolderNames = {};
while true
	[singleSubFolder, remain] = strtok(remain, ';');
	if isempty(singleSubFolder)
		break;
	end
	listOfFolderNames = [listOfFolderNames singleSubFolder];
end
numberOfFolders = length(listOfFolderNames)

% Process all image files in those folders.
for k = 1 : numberOfFolders
	% Get this folder and print it out.
	thisFolder = listOfFolderNames{k};
	fprintf('Processing folder %s\n', thisFolder);
	
	% Get PNG files.
	filePattern = sprintf('%s/*.png', thisFolder);
	baseFileNames = dir(filePattern);
	% Add on TIF files.
	filePattern = sprintf('%s/*.bmp', thisFolder);
	baseFileNames = [baseFileNames; dir(filePattern)];
	% Add on JPG files.
	filePattern = sprintf('%s/*.jpg', thisFolder);
	baseFileNames = [baseFileNames; dir(filePattern)];
	numberOfImageFiles = length(baseFileNames);
	% Now we have a list of all files in this folder.
	
	if numberOfImageFiles >= 1
		% Go through all those image files.
        dirname = ['tiled'];
        mkdir(thisFolder, dirname);
		for f = 1 : numberOfImageFiles
			fullFileName = fullfile(thisFolder, baseFileNames(f).name);
            fprintf('     Processing %s.\n', baseFileNames(f).name);
            [~,name,~] = fileparts(baseFileNames(f).name);
            tic;
            
            tile_image(fullFileName, [thisFolder '\' dirname], name);
            time = toc;
            fprintf('           Took %d seconds\n', time);
			
		end
	else
		fprintf('     Folder %s has no image files in it.\n', thisFolder);
	end
end
