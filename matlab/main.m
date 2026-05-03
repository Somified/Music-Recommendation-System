% FILE: main.m
% Linear Algebra Music Recommendation System
% =========================================================================
clear; clc; close all;

%% ── 0. Load data ─────────────────────────────────────────────────────────
[S, names, R, users] = load_data();

%% ── 1. Normalise feature matrix ──────────────────────────────────────────
S_norm = normalise(S);

%% ── 2. Choose query song ─────────────────────────────────────────────────
QUERY_SONG = 'Blinding Lights';   % <-- change if needed

query_idx = find(strcmpi(names, QUERY_SONG), 1);
if isempty(query_idx)
    error('Song "%s" not found.', QUERY_SONG);
end

fprintf('Query song: "%s" (index %d)\n', names{query_idx}, query_idx);

%% ── 3. Pillar 1 — Similarity ─────────────────────────────────────────────
[p1_scores, p1_idx] = pillar1_similarity(S_norm, query_idx);

%% ── 4. Pillar 2 — Taste Vector ───────────────────────────────────────────
if ~isempty(R)
    p2_scores = pillar2_taste(S_norm, R);
else
    warning('No ratings → Pillar 2 = 0');
    p2_scores = zeros(size(S_norm,1),1);
end

%% ── 5. Pillar 3 — Ratings ────────────────────────────────────────────────
if ~isempty(R)
    p3_scores = pillar3_ratings(R);
else
    warning('No ratings → Pillar 3 = 0');
    p3_scores = zeros(size(S_norm,1),1);
end

%% ── 6. Score Fusion ─────────────────────────────────────────────────────
alpha = 0.5;
beta  = 0.3;
gamma = 0.2;

assert(abs(alpha + beta + gamma - 1) < 1e-9, 'Weights must sum to 1');

final_scores = alpha * p1_scores(:) + ...
               beta  * p2_scores(:) + ...
               gamma * p3_scores(:);

%% ── 7. Top Recommendations ──────────────────────────────────────────────
[sorted_scores, sorted_idx] = sort(final_scores, 'descend');

% Remove query song
mask = sorted_idx ~= query_idx;
sorted_idx = sorted_idx(mask);
sorted_scores = sorted_scores(mask);

fprintf('\nTop Recommendations:\n');
for k = 1:min(10, length(sorted_idx))
    fprintf('%2d. %-30s  %.4f\n', ...
        k, names{sorted_idx(k)}, sorted_scores(k));
end

%% ── 8. Soulmates ────────────────────────────────────────────────────────
if ~isempty(R) && size(R,1) >= 2
    [soulmate_matrix, ~, ~] = find_soulmates(R, users);
else
    soulmate_matrix = [];
end

%% ── 9. Save Results ─────────────────────────────────────────────────────
results_tbl = table(names(sorted_idx(1:min(10,end))), ...
                    sorted_scores(1:min(10,end)), ...
                    'VariableNames', {'Song', 'Score'});

writetable(results_tbl, '../data/results.csv');
fprintf('\nSaved results to data/results.csv\n');

%% ── 10. Visualise ───────────────────────────────────────────────────────
visualise(S_norm, names, final_scores, p1_scores, p1_idx, ...
          query_idx, soulmate_matrix, users);

fprintf('\nDone.\n');