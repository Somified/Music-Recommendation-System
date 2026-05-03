% FILE: load_data.m
% Loads songs feature matrix S, song names, ratings matrix R, and usernames.
% =========================================================================

function [S, names, R, users] = load_data()

    %% ── Song feature matrix ─────────────────────────────────────────────
    songs_tbl = readtable('../data/songs.csv');

    % Song names
    names = songs_tbl.name;

    % Feature matrix (adjust if your CSV columns differ)
    S = [songs_tbl.tempo, ...
         songs_tbl.energy, ...
         songs_tbl.danceability, ...
         songs_tbl.valence];

    fprintf('Loaded %d songs with %d features.\n', size(S,1), size(S,2));


    %% ── Ratings matrix R (users × songs) ───────────────────────────────
    if isfile('../data/ratings.csv')
        ratings_tbl = readtable('../data/ratings.csv');

        users = ratings_tbl{:,1};        % usernames
        R     = ratings_tbl{:,2:end};    % ratings

        R = double(R);

        fprintf('Loaded ratings matrix: %d users × %d songs.\n', ...
                size(R,1), size(R,2));

        % Align R with number of songs
        n_songs = size(S, 1);
        if size(R, 2) ~= n_songs
            warning('ratings.csv mismatch. Fixing dimensions.');

            if size(R,2) > n_songs
                R = R(:, 1:n_songs);
            else
                R = [R, zeros(size(R,1), n_songs - size(R,2))];
            end
        end

    else
        warning('ratings.csv not found. Using empty R.');
        R     = zeros(0, size(S,1));
        users = {};
    end

end