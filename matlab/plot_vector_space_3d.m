% =========================================================================
% FILE: plot_vector_space_3d.m
% GRAPH 1 — 3D Vector Space Visualisation
%
% Demonstrates:
%   - Each song as a vector in feature space (Energy, Danceability, Valence)
%   - Seed songs selected by the user
%   - Computed taste centroid  v̄ = (s1 + s2 + ... + sn) / n
%   - Recommended songs
%   - Lines from centroid to each recommendation (cosine / euclidean paths)
%
% LA concepts shown:
%   Vectors · Linear Combination · Centroid · Distance in ℝ³
%
% Usage:
%   Run standalone, or call from main.m after defining seed_indices
%   and rec_indices.  Standalone mode auto-picks seeds + recs for demo.
% =========================================================================

function plot_vector_space_3d(S_norm, names, seed_indices, rec_indices)

    % ── Palette (matches Melodix Macaron theme) ───────────────────────────
    C_ALL   = [0.85  0.80  0.70];   % warm beige   — background songs
    C_SEED  = [0.20  0.55  0.20];   % forest green — seed songs
    C_REC   = [0.78  0.13  0.31];   % old rose     — recommendations
    C_CENT  = [0.93  0.37  0.60];   % brilliant rose — centroid
    C_LINE  = [0.93  0.37  0.60];   % line colour (centroid → rec)
    C_BG    = [0.98  0.95  0.89];   % yucca white background

    % ── Feature column indices in S_norm ─────────────────────────────────
    % Assumes S_norm columns are: [energy, danceability, valence, ...]
    % Adjust IDX_* if your column order differs.
    IDX_ENERGY       = 1;
    IDX_DANCEABILITY = 2;
    IDX_VALENCE      = 3;

    if size(S_norm, 2) < 3
        error('S_norm must have at least 3 columns (energy, danceability, valence).');
    end

    % ── Standalone demo mode (no arguments passed) ────────────────────────
    if nargin < 3 || isempty(seed_indices)
        fprintf('[plot_vector_space_3d] Standalone demo — auto-selecting seeds & recs.\n');
        n_all        = size(S_norm, 1);
        seed_indices = randsample(n_all, min(4, n_all));
        % Compute centroid and pick top-5 cosine-similar songs
        centroid_tmp = mean(S_norm(seed_indices, :), 1)';
        cos_tmp      = cosine_similarity_all(S_norm, centroid_tmp);
        cos_tmp(seed_indices) = -1;
        [~, order]   = sort(cos_tmp, 'descend');
        rec_indices  = order(1:min(5, n_all));
    end

    if nargin < 4 || isempty(rec_indices)
        % Compute centroid and pick top-5 if recs not provided
        centroid_tmp = mean(S_norm(seed_indices, :), 1)';
        cos_tmp      = cosine_similarity_all(S_norm, centroid_tmp);
        cos_tmp(seed_indices) = -1;
        [~, order]   = sort(cos_tmp, 'descend');
        rec_indices  = order(1:min(5, size(S_norm,1)));
    end

    % ── Extract 3D coordinates ────────────────────────────────────────────
    X_all  = S_norm(:, IDX_ENERGY);
    Y_all  = S_norm(:, IDX_DANCEABILITY);
    Z_all  = S_norm(:, IDX_VALENCE);

    % Compute taste centroid in 3D projection
    centroid_full = mean(S_norm(seed_indices, :), 1);
    cx = centroid_full(IDX_ENERGY);
    cy = centroid_full(IDX_DANCEABILITY);
    cz = centroid_full(IDX_VALENCE);

    % ── Build exclusion mask (remove seeds + recs from background cloud) ──
    special = union(seed_indices(:)', rec_indices(:)');
    bg_mask = true(size(S_norm, 1), 1);
    bg_mask(special) = false;

    % ── Figure setup ─────────────────────────────────────────────────────
    fig = figure('Name', 'Melodix — 3D Vector Space', ...
                 'NumberTitle', 'off', ...
                 'Color', C_BG, ...
                 'Position', [100 100 1020 780]);

    ax = axes('Parent', fig, 'Color', C_BG);
    hold(ax, 'on');

    % ── 1. Background songs (all) ─────────────────────────────────────────
    scatter3(ax, X_all(bg_mask), Y_all(bg_mask), Z_all(bg_mask), ...
             18, ...
             'MarkerFaceColor', C_ALL, ...
             'MarkerEdgeColor', 'none', ...
             'MarkerFaceAlpha', 0.35, ...
             'DisplayName', sprintf('All Songs (n=%d)', sum(bg_mask)));

    % ── 2. Recommended songs ──────────────────────────────────────────────
    scatter3(ax, X_all(rec_indices), Y_all(rec_indices), Z_all(rec_indices), ...
             90, ...
             'MarkerFaceColor', C_REC, ...
             'MarkerEdgeColor', [0.50 0.05 0.15], ...
             'LineWidth', 1.2, ...
             'MarkerFaceAlpha', 0.85, ...
             'DisplayName', sprintf('Recommendations (n=%d)', length(rec_indices)));

    % ── 3. Lines from centroid to each recommended song ───────────────────
    for k = 1:length(rec_indices)
        idx = rec_indices(k);
        plot3(ax, [cx X_all(idx)], [cy Y_all(idx)], [cz Z_all(idx)], ...
              '-', 'Color', [C_LINE 0.55], 'LineWidth', 1.0, ...
              'HandleVisibility', 'off');
    end

    % ── 4. Seed songs ─────────────────────────────────────────────────────
    scatter3(ax, X_all(seed_indices), Y_all(seed_indices), Z_all(seed_indices), ...
             110, ...
             'MarkerFaceColor', C_SEED, ...
             'MarkerEdgeColor', [0.08 0.30 0.08], ...
             'LineWidth', 1.4, ...
             'MarkerFaceAlpha', 0.90, ...
             'DisplayName', sprintf('Seed Songs (n=%d)', length(seed_indices)));

    % ── 5. Taste centroid ─────────────────────────────────────────────────
    scatter3(ax, cx, cy, cz, ...
             280, ...
             'MarkerFaceColor', C_CENT, ...
             'MarkerEdgeColor', [0.50 0.05 0.25], ...
             'LineWidth', 2.2, ...
             'Marker', 'p', ...           % pentagram
             'DisplayName', 'Taste Centroid  v̄');

    % ── 6. Centroid label ─────────────────────────────────────────────────
    text(ax, cx + 0.015, cy + 0.015, cz + 0.015, ...
         sprintf('v̄ = (%.2f, %.2f, %.2f)', cx, cy, cz), ...
         'FontSize', 8, 'FontWeight', 'bold', ...
         'Color', [0.50 0.05 0.25], ...
         'Interpreter', 'none');

    % ── 7. Seed song name labels ───────────────────────────────────────────
    if ~isempty(names)
        for k = 1:length(seed_indices)
            idx  = seed_indices(k);
            lbl  = names{idx};
            if length(lbl) > 22, lbl = [lbl(1:20) '…']; end
            text(ax, X_all(idx) + 0.012, Y_all(idx), Z_all(idx), ...
                 lbl, 'FontSize', 7, 'Color', [0.08 0.30 0.08], ...
                 'FontWeight', 'bold', 'Interpreter', 'none');
        end
    end

    % ── 8. Recommended song name labels ───────────────────────────────────
    if ~isempty(names)
        for k = 1:length(rec_indices)
            idx = rec_indices(k);
            lbl = names{idx};
            if length(lbl) > 22, lbl = [lbl(1:20) '…']; end
            text(ax, X_all(idx) + 0.012, Y_all(idx), Z_all(idx), ...
                 lbl, 'FontSize', 6.5, 'Color', [0.55 0.08 0.20], ...
                 'Interpreter', 'none');
        end
    end

    % ── Axes, labels, title ───────────────────────────────────────────────
    xlabel(ax, 'Energy  →', 'FontSize', 13, 'FontWeight', 'bold', ...
           'Color', [0.29 0.06 0.13]);
    ylabel(ax, 'Danceability  →', 'FontSize', 13, 'FontWeight', 'bold', ...
           'Color', [0.29 0.06 0.13]);
    zlabel(ax, 'Valence  →', 'FontSize', 13, 'FontWeight', 'bold', ...
           'Color', [0.29 0.06 0.13]);

    title(ax, {'Melodix — 3D Feature-Space Vector Visualisation'; ...
               'Centroid-Based Recommendation Logic'}, ...
          'FontSize', 15, 'FontWeight', 'bold', 'Color', [0.29 0.06 0.13]);

    % Subtitle with centroid formula
    subtitle_str = sprintf( ...
        'v̄_{taste} = (s_1 + s_2 + ... + s_%d) / %d   |   Lines show cosine / Euclidean similarity path', ...
        length(seed_indices), length(seed_indices));
    subtitle(ax, subtitle_str, 'FontSize', 9, 'Color', [0.60 0.40 0.45]);

    grid(ax, 'on');
    ax.GridColor       = [0.75 0.68 0.58];
    ax.GridAlpha       = 0.45;
    ax.XColor          = [0.45 0.30 0.25];
    ax.YColor          = [0.45 0.30 0.25];
    ax.ZColor          = [0.45 0.30 0.25];
    ax.TickDir         = 'out';
    ax.FontSize        = 10;
    ax.Box             = 'off';

    xlim(ax, [0 1]); ylim(ax, [0 1]); zlim(ax, [0 1]);

    % ── Legend ────────────────────────────────────────────────────────────
    lgd = legend(ax, 'Location', 'northeast', 'FontSize', 9);
    lgd.Box      = 'on';
    lgd.Color    = [0.98 0.95 0.89];
    lgd.EdgeColor= [0.85 0.75 0.65];
    lgd.TextColor= [0.29 0.06 0.13];

    % ── Annotation box ────────────────────────────────────────────────────
    annotation('textbox', [0.01 0.01 0.40 0.07], ...
               'String', { ...
                   'LA Concepts:  Vectors in ℝ³  ·  Linear Combination (centroid)  ·  Cosine Similarity  ·  Euclidean Distance'}, ...
               'FitBoxToText', 'on', 'EdgeColor', [0.85 0.75 0.65], ...
               'BackgroundColor', [0.98 0.95 0.89], ...
               'FontSize', 8, 'Color', [0.45 0.25 0.20]);

    % ── 3D view angle ─────────────────────────────────────────────────────
    view(ax, 35, 22);
    hold(ax, 'off');

    % Save
    saveas(fig, '../data/graph1_vector_space_3d.png');
    fprintf('[Graph 1] Saved → data/graph1_vector_space_3d.png\n');
end

% ── Helper: cosine similarity of all rows in S against query vector ──────
function sims = cosine_similarity_all(S, q)
    q_norm = norm(q);
    if q_norm < 1e-12, sims = zeros(size(S,1),1); return; end
    row_norms       = vecnorm(S, 2, 2);
    row_norms(row_norms < 1e-12) = 1;
    sims            = (S * q) ./ (row_norms * q_norm);
    sims            = max(0, sims);
end