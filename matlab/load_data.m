% FILE: load_data.m
% Reads songs.csv and returns the feature matrix S and song names.
% ═══════════════════════════════════════════════════════════════════════
function [S, names] = load_data()
 
    T     = readtable('songs.csv');
    names = T.name;          % cell array of song name strings
    S     = T{:, 3:7};       % columns: energy, danceability, valence,
                              %          acousticness, tempo
                              % Result: (num_songs x 5) numeric matrix
 
    fprintf('Loaded %d songs with %d features each.\n', size(S,1), size(S,2));
end
 
 
