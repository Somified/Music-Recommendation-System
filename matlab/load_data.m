function [S, names] = load_data(songs_file)

    if nargin < 1
        songs_file = fullfile('..', 'data', 'songs.csv');
    end

    T     = readtable(songs_file);
    names = cellstr(T.name);
    S     = T{:, 3:7};

    fprintf('Loaded %d songs with %d features each.\n', size(S,1), size(S,2));
end