% FILE: main.m
% Linear Algebra Music Recommendation System
% Hybrid engine: 0.6*cosine + 0.4*euclidean_similarity
% Exports results to CSV and JSON for Python/Streamlit integration.
% =========================================================================
clear; clc; close all;

%% ── 0. Load data ──────────────────────────────────────────────────────────
[S, names, R, users] = load_data();
n_songs = size(S, 1);

%% ── 1. Normalise feature matrix ───────────────────────────────────────────
S_norm = normalise(S);

%% ── 2. Choose query song ──────────────────────────────────────────────────
QUERY_SONG = 'Blinding Lights';    % <-- edit to any song in your dataset
TOP_N      = 10;

query_idx = find(strcmpi(names, QUERY_SONG), 1);
if isempty(query_idx)
    error('Song "%s" not found. Check spelling against songs.csv.', QUERY_SONG);
end
fprintf('Query song : "%s"  (index %d / %d)\n', names{query_idx}, query_idx, n_songs);

%% ── 3. Pillar 1 — Hybrid Similarity ──────────────────────────────────────
% Formula: hybrid(i) = 0.6 * cosine(i) + 0.4 * (1 / (1 + euclidean(i)))
W_COS = 0.6;
W_EUC = 0.4;

[hybrid_scores, cos_scores, euc_scores, hybrid_idx, dot_prods, norms_songs] = ...
    hybrid_similarity(S_norm, query_idx, W_COS, W_EUC);

% Legacy cosine-only for comparison
[p1_scores, p1_idx] = pillar1_similarity(S_norm, query_idx);

%% ── 4. Pillar 2 — User Taste Vector ──────────────────────────────────────
if ~isempty(R)
    p2_scores = pillar2_taste(S_norm, R);
else
    warning('No ratings data — Pillar 2 set to zero.');
    p2_scores = zeros(n_songs, 1);
end

%% ── 5. Pillar 3 — Rating Matrix ──────────────────────────────────────────
if ~isempty(R)
    p3_scores = pillar3_ratings(R);
else
    warning('No ratings data — Pillar 3 set to zero.');
    p3_scores = zeros(n_songs, 1);
end

%% ── 6. Score Fusion — Linear Combination ─────────────────────────────────
alpha = 0.5;   % Pillar 1 (hybrid similarity)
beta  = 0.3;   % Pillar 2 (taste vector)
gamma = 0.2;   % Pillar 3 (rating matrix)
assert(abs(alpha + beta + gamma - 1) < 1e-9, 'Weights must sum to 1.');

fprintf('Score fusion: alpha=%.2f*hybrid  +  beta=%.2f*taste  +  gamma=%.2f*ratings\n', ...
        alpha, beta, gamma);

final_scores = alpha * hybrid_scores(:) + beta * p2_scores(:) + gamma * p3_scores(:);
final_scores(query_idx) = 0;

%% ── 7. Rank and print ─────────────────────────────────────────────────────
[sorted_final, sorted_idx] = sort(final_scores, 'descend');
mask         = sorted_idx ~= query_idx;
sorted_idx   = sorted_idx(mask);
sorted_final = sorted_final(mask);

fprintf('\n===================================================================\n');
fprintf('  TOP-%d RECOMMENDATIONS FOR: "%s"\n', TOP_N, names{query_idx});
fprintf('  Engine: %.0f%% cosine + %.0f%% euclidean (hybrid Pillar 1)\n', W_COS*100, W_EUC*100);
fprintf('===================================================================\n');
fprintf('  %-4s  %-35s  %8s  %8s  %8s\n', 'Rank', 'Song', 'Hybrid', 'Cosine', 'Final');
fprintf('  %s\n', repmat('-', 1, 70));
for k = 1:min(TOP_N, length(sorted_idx))
    idx = sorted_idx(k);
    fprintf('  %-4d  %-35s  %8.4f  %8.4f  %8.4f\n', ...
            k, names{idx}, hybrid_scores(idx), cos_scores(idx), sorted_final(k));
end
fprintf('===================================================================\n\n');

%% ── 8. LA Transparency — dot products & norms ────────────────────────────
fprintf('-- LA Transparency: dot products & norms (top 5) --\n');
fprintf('  Query L2 norm: %.4f\n\n', norm(S_norm(query_idx,:)));
fprintf('  %-35s  %10s  %10s  %10s  %10s\n', 'Song','Dot Prod','||s||','Cosine','Euc Sim');
fprintf('  %s\n', repmat('-',1,75));
for k = 1:min(5, length(sorted_idx))
    idx = sorted_idx(k);
    fprintf('  %-35s  %10.4f  %10.4f  %10.4f  %10.4f\n', ...
            names{idx}, dot_prods(idx), norms_songs(idx), cos_scores(idx), euc_scores(idx));
end
fprintf('\n');

%% ── 9. Correlation matrices ───────────────────────────────────────────────
if ~isempty(R) && size(R,1) >= 2
    fprintf('Building correlation matrices...\n');
    C_songs = corr(R);
    C_users = corr(R');
    fprintf('  C_songs: %dx%d  |  C_users: %dx%d\n', ...
            size(C_songs,1),size(C_songs,2),size(C_users,1),size(C_users,2));
end

%% ── 10. Export: CSV ──────────────────────────────────────────────────────
top_k      = min(TOP_N, length(sorted_idx));
top_idx    = sorted_idx(1:top_k);
ranks      = (1:top_k)';
top_names  = names(top_idx);
top_final  = sorted_final(1:top_k);
top_hybrid = hybrid_scores(top_idx);
top_cos    = cos_scores(top_idx);
top_euc    = euc_scores(top_idx);
top_dot    = dot_prods(top_idx);
top_norms  = norms_songs(top_idx);

results_tbl = table(ranks, top_names, top_final, top_hybrid, top_cos, top_euc, top_dot, top_norms, ...
    'VariableNames', {'Rank','Song','FinalScore','HybridScore','CosineScore', ...
                      'EuclideanSim','DotProduct','SongNorm'});
csv_path = '../data/matlab_results.csv';
writetable(results_tbl, csv_path);
fprintf('CSV saved  -> %s\n', csv_path);

%% ── 11. Export: JSON (primary format for Streamlit) ──────────────────────
json_path = '../data/matlab_results.json';
fid = fopen(json_path, 'w');
if fid == -1
    warning('Could not open %s for writing.', json_path);
else
    fprintf(fid, '{\n');
    fprintf(fid, '  "query_song": "%s",\n',     strrep(names{query_idx},'"','\"'));
    fprintf(fid, '  "query_index": %d,\n',       query_idx - 1);
    fprintf(fid, '  "query_norm": %.6f,\n',       norm(S_norm(query_idx,:)));
    fprintf(fid, '  "w_cos": %.2f,\n',            W_COS);
    fprintf(fid, '  "w_euc": %.2f,\n',            W_EUC);
    fprintf(fid, '  "alpha": %.2f,\n',            alpha);
    fprintf(fid, '  "beta": %.2f,\n',             beta);
    fprintf(fid, '  "gamma": %.2f,\n',            gamma);
    fprintf(fid, '  "n_songs_total": %d,\n',      n_songs);
    fprintf(fid, '  "recommendations": [\n');

    for k = 1:top_k
        idx      = top_idx(k);
        song_esc = strrep(names{idx}, '"', '\"');
        fprintf(fid, '    {\n');
        fprintf(fid, '      "rank": %d,\n',            k);
        fprintf(fid, '      "song": "%s",\n',           song_esc);
        fprintf(fid, '      "index_0based": %d,\n',     idx - 1);
        fprintf(fid, '      "final_score": %.6f,\n',    top_final(k));
        fprintf(fid, '      "hybrid_score": %.6f,\n',   top_hybrid(k));
        fprintf(fid, '      "cosine_score": %.6f,\n',   top_cos(k));
        fprintf(fid, '      "euclidean_sim": %.6f,\n',  top_euc(k));
        fprintf(fid, '      "dot_product": %.6f,\n',    top_dot(k));
        fprintf(fid, '      "song_norm": %.6f\n',        top_norms(k));
        if k < top_k
            fprintf(fid, '    },\n');
        else
            fprintf(fid, '    }\n');
        end
    end

    fprintf(fid, '  ]\n');
    fprintf(fid, '}\n');
    fclose(fid);
    fprintf('JSON saved -> %s\n', json_path);
end

%% ── 12. Visualise ────────────────────────────────────────────────────────
visualise(S_norm, names, final_scores, hybrid_scores, hybrid_idx, query_idx, [], {});

fprintf('\nDone! Run: streamlit run python/app.py\n');