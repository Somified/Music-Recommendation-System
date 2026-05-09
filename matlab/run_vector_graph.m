clc; clear; close all;

% Go to matlab folder
cd('C:/Users/saumy/OneDrive/Desktop/Linear Algebra/Linear algebra music system/matlab')

% Load CSV
songs_tbl = readtable('../data/songs.csv');

% Select features
features = {
    'energy',...
    'danceability',...
    'valence',...
    'acousticness',...
    'speechiness',...
    'instrumentalness',...
    'liveness',...
    'tempo'
};

% Build matrix
S = songs_tbl{:, features};

% Z-score normalization
S_norm = zscore(S);

% Song names
names = songs_tbl.track_name;

% Example seed songs
seed_indices = [1 5 10 15];

% Example recommendations
rec_indices = [20 25 30 35 40];

% RUN GRAPH
plot_vector_space_3d(S_norm, names, seed_indices, rec_indices);