% FILE: main.m
% Runs the full pipeline. This is the only file you need to execute.
%
% HOW TO RUN:
%   1. Make sure MATLAB's working folder is set to your matlab/ folder
%   2. Confirm songs.csv and ratings.csv are in ../data/
%   3. Type:  main   (in the MATLAB command window)
% ══════════════════════════════════════════════════════════════════════

clear; clc;

% ── Point MATLAB to the data folder ──────────────────────────────────
data_path    = fullfile('..', 'data');
songs_file   = fullfile(data_path, 'songs.csv');
ratings_file = fullfile(data_path, 'ratings.csv');

% ── STEP 1: Load data ─────────────────────────────────────────────────
T     = readtable(songs_file);
names = T.name;
S_raw = T{:, 3:7};    % energy, danceability, valence, acousticness, tempo

fprintf('\nLoaded %d songs with %d features.\n', size(S_raw,1), size(S_raw,2));

% ── STEP 2: Normalise ─────────────────────────────────────────────────
col_min = min(S_raw);
col_max = max(S_raw);
S = (S_raw - col_min) ./ (col_max - col_min);

fprintf('Features normalised to [0,1].\n');

% ── STEP 3: Show song list ────────────────────────────────────────────
fprintf('\nAvailable songs:\n');
for i = 1:length(names)
    fprintf('  %2d.  %s\n', i, names{i});
end

% ── Hardcoded query — change this number to try different songs ───────
% 1 = Blinding Lights
query_idx = 1;
fprintf('\nQuery song: "%s"\n', names{query_idx});

% ── STEP 4: Pillar 1 — cosine similarity ─────────────────────────────
[p1_scores, p1_idx] = pillar1_similarity(S, query_idx);

fprintf('\n── Pillar 1: Songs similar to "%s" ──\n', names{query_idx});
num_results = min(5, length(p1_idx) - 1);
for k = 1:num_results
    fprintf('  %d.  %-30s  similarity: %.4f\n', ...
            k, names{p1_idx(k+1)}, p1_scores(k+1));
end

% ── STEP 5: Pillar 2 — taste vector ──────────────────────────────────
liked = [1, 4, 8, 11];

fprintf('\nLiked songs: ');
for i = 1:length(liked)
    fprintf('"%s"  ', names{liked(i)});
end
fprintf('\n');

[~, p2_scores, p2_idx] = pillar2_taste(S, liked);

fprintf('\n── Pillar 2: Songs matching taste profile ──\n');
for k = 1:min(5, length(p2_idx))
    fprintf('  %d.  %-30s  match: %.4f\n', ...
            k, names{p2_idx(k)}, p2_scores(k));
end

% ── STEP 6: Pillar 3 — rating matrix ─────────────────────────────────
R_table  = readtable(ratings_file);
real_row = R_table.rating';
num_songs = length(names);

rng(42);
R = [
    real_row;
    randi([2,5], 1, num_songs) .* double(rand(1, num_songs) > 0.4);
    randi([1,5], 1, num_songs) .* double(rand(1, num_songs) > 0.5);
    randi([3,5], 1, num_songs) .* double(rand(1, num_songs) > 0.3);
];

[p3_scores, p3_idx] = pillar3_ratings(R, 1);

fprintf('\n── Pillar 3: Predicted ratings ──\n');
for k = 1:min(5, length(p3_idx))
    fprintf('  %d.  %-30s  predicted: %.4f\n', ...
            k, names{p3_idx(k)}, p3_scores(k));
end

% ── STEP 7: Score fusion ──────────────────────────────────────────────
alpha = 0.5;
beta  = 0.3;
gamma = 0.2;

p1_aligned = zeros(length(names), 1);
p1_aligned(p1_idx) = p1_scores;

p2_aligned = zeros(length(names), 1);
p2_aligned(p2_idx) = p2_scores;

p3_aligned = zeros(length(names), 1);
p3_aligned(p3_idx) = p3_scores;

final_scores = alpha * p1_aligned + beta * p2_aligned + gamma * p3_aligned;

[final_sorted, final_idx] = sort(final_scores, 'descend');

fprintf('\n══════════════════════════════════════════════\n');
fprintf('  FINAL RECOMMENDATIONS (all pillars fused)\n');
fprintf('══════════════════════════════════════════════\n');
for k = 1:min(5, length(final_idx))
    fprintf('  %d.  %-30s  score: %.4f\n', ...
            k, names{final_idx(k)}, final_sorted(k));
end
fprintf('══════════════════════════════════════════════\n');

% ── STEP 8: Export results.csv ────────────────────────────────────────
results = table(names, final_scores, p1_aligned, p2_aligned, p3_aligned, ...
    'VariableNames', {'song','final_score','pillar1','pillar2','pillar3'});

results_path = fullfile(data_path, 'results.csv');
writetable(results, results_path);
fprintf('\nSaved results to %s\n', results_path);
fprintf('Python Streamlit app can now read this file.\n');

% ── STEP 9: Visualisations ────────────────────────────────────────────
visualise(S, names, final_scores, p1_scores, p1_idx, query_idx);