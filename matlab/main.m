clear; clc;

data_path    = fullfile('..', 'data');
songs_file   = fullfile(data_path, 'songs.csv');
ratings_file = fullfile(data_path, 'ratings.csv');

[S_raw, names] = load_data(songs_file);
num_songs      = length(names);

fprintf('\nLoaded %d songs with %d features.\n', size(S_raw,1), size(S_raw,2));

S = normalise(S_raw);

fprintf('\nAvailable songs:\n');
for i = 1:num_songs
    fprintf('  %2d.  %s\n', i, names{i});
end

query_idx = 1;
fprintf('\nQuery song: "%s"\n', names{query_idx});

[p1_scores, p1_idx] = pillar1_similarity(S, query_idx);

fprintf('\n── Pillar 1: Songs similar to "%s" ──\n', names{query_idx});
num_results = min(5, length(p1_idx) - 1);
for k = 1:num_results
    fprintf('  %d.  %-30s  similarity: %.4f\n', ...
            k, names{p1_idx(k+1)}, p1_scores(k+1));
end

liked = [1, 4, 8, 11];
liked = liked(liked >= 1 & liked <= num_songs);

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

R_table = readtable(ratings_file);

assert(height(R_table) == num_songs, ...
    'Mismatch: songs.csv has %d songs but ratings.csv has %d rows.', ...
    num_songs, height(R_table));

rated_count = floor(num_songs / 2);
real_row    = zeros(1, num_songs);
real_row(1 : rated_count) = R_table.rating(1 : rated_count)';

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

alpha = 0.5;
beta  = 0.3;
gamma = 0.2;

p1_aligned             = zeros(num_songs, 1);
p1_aligned(p1_idx)     = p1_scores;

p2_aligned             = zeros(num_songs, 1);
p2_aligned(p2_idx)     = p2_scores;

p3_aligned             = zeros(num_songs, 1);
p3_aligned(p3_idx)     = p3_scores;

final_scores            = alpha * p1_aligned + beta * p2_aligned + gamma * p3_aligned;
final_scores(query_idx) = 0;

[final_sorted, final_idx] = sort(final_scores, 'descend');

fprintf('\n══════════════════════════════════════════════\n');
fprintf('  FINAL RECOMMENDATIONS (all pillars fused)\n');
fprintf('══════════════════════════════════════════════\n');
for k = 1:min(5, length(final_idx))
    fprintf('  %d.  %-30s  score: %.4f\n', ...
            k, names{final_idx(k)}, final_sorted(k));
end
fprintf('══════════════════════════════════════════════\n');

results = table(names, final_scores, p1_aligned, p2_aligned, p3_aligned, ...
    'VariableNames', {'song','final_score','pillar1','pillar2','pillar3'});

results_path = fullfile(data_path, 'results.csv');
writetable(results, results_path);
fprintf('\nSaved results to %s\n', results_path);

visualise(S, names, final_scores, p1_scores, p1_idx, query_idx);