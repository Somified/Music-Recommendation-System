% =========================================================================
% FILE: plot_normalisation_comparison.m
% GRAPH 2 — Before vs After Z-Score Normalisation
%
% Demonstrates WHY normalisation is essential before computing similarity.
% Shows 8 audio features in raw scale vs standardised (z-score) scale
% using four complementary subplots:
%
%   Row 1 (left)  — Raw feature distributions (overlaid violin/box)
%   Row 1 (right) — Z-score standardised distributions
%   Row 2 (left)  — Feature range table (min, max, std before/after)
%   Row 2 (right) — Mean ± 1σ bar chart before and after
%
% LA concept: Standardisation   z = (x − μ) / σ
%             Ensures all features live on the same scale before
%             computing dot products and norms.
%
% Usage:
%   plot_normalisation_comparison(S, feat_names)
%   or run standalone (loads data/songs.csv automatically).
% =========================================================================

function plot_normalisation_comparison(S, feat_names)

    % ── Palette ───────────────────────────────────────────────────────────
    C_BG      = [0.98  0.95  0.89];   % yucca white
    C_RAW     = [0.20  0.55  0.20];   % forest green  — raw
    C_NORM    = [0.78  0.13  0.31];   % old rose      — normalised
    C_ZERO    = [0.93  0.37  0.60];   % brilliant rose — zero line
    C_TEXT    = [0.29  0.06  0.13];   % bordeaux
    C_GRID    = [0.80  0.73  0.63];
    C_BOX_RAW = [0.80  0.90  0.80];   % light green fill
    C_BOX_NRM = [0.97  0.82  0.87];   % light rose fill

    % ── Standalone mode ───────────────────────────────────────────────────
    if nargin < 1
        fprintf('[plot_normalisation_comparison] Loading data/songs.csv...\n');
        tbl = readtable('../data/songs.csv');

        % Auto-detect column names (Kaggle dataset uses track_name)
        feat_candidates = {'energy','danceability','valence','acousticness', ...
                           'speechiness','instrumentalness','liveness','tempo'};
        feat_names = {};
        S_cols     = [];
        for k = 1:length(feat_candidates)
            f = feat_candidates{k};
            if ismember(f, tbl.Properties.VariableNames)
                feat_names{end+1} = f;   %#ok<AGROW>
                S_cols = [S_cols, tbl.(f)];  %#ok<AGROW>
            end
        end
        S = double(S_cols);
        if isempty(S)
            error('Could not find audio feature columns in songs.csv.');
        end
        fprintf('[plot_normalisation_comparison] Found %d features: %s\n', ...
                length(feat_names), strjoin(feat_names, ', '));
    end

    if nargin < 2 || isempty(feat_names)
        feat_names = arrayfun(@(i) sprintf('Feature %d', i), ...
                              1:size(S,2), 'UniformOutput', false);
    end

    n_feats = length(feat_names);
    S       = double(S(:, 1:n_feats));

    % ── Remove rows with any NaN ──────────────────────────────────────────
    S = S(~any(isnan(S), 2), :);
    n_songs = size(S, 1);
    fprintf('[plot_normalisation_comparison] Using %d songs × %d features.\n', ...
            n_songs, n_feats);

    % ── Z-score standardisation ───────────────────────────────────────────
    mu      = mean(S, 1);          % (1 × n_feats)
    sigma   = std(S, 0, 1);        % (1 × n_feats)
    sigma(sigma < 1e-9) = 1;       % guard constant features
    S_z     = (S - mu) ./ sigma;   % (n_songs × n_feats)

    % ── Pre-compute stats ─────────────────────────────────────────────────
    raw_min  = min(S,  [], 1);
    raw_max  = max(S,  [], 1);
    raw_std  = std(S,  0, 1);
    raw_mean = mean(S, 1);
    z_min    = min(S_z,  [], 1);
    z_max    = max(S_z,  [], 1);
    z_std    = std(S_z,  0, 1);

    % Subsample for plotting speed (keep ≤ 2000 points)
    n_plot = min(2000, n_songs);
    idx_s  = randperm(n_songs, n_plot);
    S_s    = S(idx_s, :);
    Sz_s   = S_z(idx_s, :);

    % ── Figure ────────────────────────────────────────────────────────────
    fig = figure('Name', 'Melodix — Normalisation Comparison', ...
                 'NumberTitle', 'off', ...
                 'Color', C_BG, ...
                 'Position', [80 60 1280 840]);

    % Use a 3-row layout:
    %   Row 1: Box plots   Raw | Z-score
    %   Row 2: Std bars    Raw | Z-score
    %   Row 3: Range table (full width)

    % ══════════════════════════════════════════════════════════════════════
    % SUBPLOT 1 — Raw feature distributions
    % ══════════════════════════════════════════════════════════════════════
    ax1 = subplot(2, 2, 1);
    set(ax1, 'Color', C_BG);
    hold(ax1, 'on');

    % Violin-style jitter scatter + box for each feature
    jitter_amount = 0.18;
    for f = 1:n_feats
        x_base  = f;
        y_vals  = S_s(:, f);
        x_jit   = x_base + (rand(n_plot,1) - 0.5) * jitter_amount;

        scatter(ax1, x_jit, y_vals, 6, ...
                'MarkerFaceColor', C_BOX_RAW, ...
                'MarkerEdgeColor', 'none', ...
                'MarkerFaceAlpha', 0.4);

        % Overlay IQR box
        q25 = prctile(y_vals, 25);
        q75 = prctile(y_vals, 75);
        med = median(y_vals);
        rectangle(ax1, 'Position', [f - 0.22, q25, 0.44, q75-q25], ...
                  'FaceColor', [C_RAW 0.25], ...
                  'EdgeColor', C_RAW, 'LineWidth', 1.5);
        plot(ax1, [f-0.22, f+0.22], [med, med], '-', ...
             'Color', C_RAW, 'LineWidth', 2.0);
    end

    ax1.XTick      = 1:n_feats;
    ax1.XTickLabel = feat_names;
    ax1.XTickLabelRotation = 35;
    ax1.FontSize   = 9;
    ax1.Color      = C_BG;
    ax1.GridColor  = C_GRID;
    ax1.GridAlpha  = 0.5;
    ax1.XColor     = C_TEXT;
    ax1.YColor     = C_TEXT;
    grid(ax1, 'on');
    xlim(ax1, [0.4, n_feats + 0.6]);
    ylabel(ax1, 'Raw Feature Value', 'FontSize', 11, 'Color', C_TEXT, 'FontWeight', 'bold');
    title(ax1, {'Before Normalisation'; 'Raw feature values — incomparable scales'}, ...
          'FontSize', 12, 'Color', C_TEXT, 'FontWeight', 'bold');

    % Annotate range spread
    for f = 1:n_feats
        text(ax1, f, raw_max(f) + 0.02*(raw_max(f)-raw_min(f)+0.1), ...
             sprintf('[%.0f–%.0f]', raw_min(f), raw_max(f)), ...
             'FontSize', 6.5, 'HorizontalAlignment', 'center', ...
             'Color', [0.35 0.55 0.35], 'Interpreter', 'none');
    end
    hold(ax1, 'off');

    % ══════════════════════════════════════════════════════════════════════
    % SUBPLOT 2 — Z-score normalised distributions
    % ══════════════════════════════════════════════════════════════════════
    ax2 = subplot(2, 2, 2);
    set(ax2, 'Color', C_BG);
    hold(ax2, 'on');

    % Zero line (μ = 0 after standardisation)
    plot(ax2, [0.3, n_feats + 0.7], [0, 0], '--', ...
         'Color', [C_ZERO 0.7], 'LineWidth', 1.5, ...
         'DisplayName', 'μ = 0  (after standardisation)');

    % ±1σ band
    patch(ax2, [0.3, n_feats+0.7, n_feats+0.7, 0.3], ...
          [1, 1, -1, -1], ...
          C_ZERO, 'FaceAlpha', 0.06, 'EdgeColor', 'none', ...
          'DisplayName', '±1σ band');

    for f = 1:n_feats
        y_vals = Sz_s(:, f);
        x_jit  = f + (rand(n_plot,1) - 0.5) * jitter_amount;

        scatter(ax2, x_jit, y_vals, 6, ...
                'MarkerFaceColor', C_BOX_NRM, ...
                'MarkerEdgeColor', 'none', ...
                'MarkerFaceAlpha', 0.45);

        q25 = prctile(y_vals, 25);
        q75 = prctile(y_vals, 75);
        med = median(y_vals);
        rectangle(ax2, 'Position', [f - 0.22, q25, 0.44, q75-q25], ...
                  'FaceColor', [C_NORM 0.20], ...
                  'EdgeColor', C_NORM, 'LineWidth', 1.5);
        plot(ax2, [f-0.22, f+0.22], [med, med], '-', ...
             'Color', C_NORM, 'LineWidth', 2.0);

        % Annotate actual z-score range
        text(ax2, f, max(y_vals) + 0.10, ...
             sprintf('σ=%.2f', z_std(f)), ...
             'FontSize', 6.5, 'HorizontalAlignment', 'center', ...
             'Color', [0.55 0.10 0.25], 'Interpreter', 'none');
    end

    ax2.XTick      = 1:n_feats;
    ax2.XTickLabel = feat_names;
    ax2.XTickLabelRotation = 35;
    ax2.FontSize   = 9;
    ax2.Color      = C_BG;
    ax2.GridColor  = C_GRID;
    ax2.GridAlpha  = 0.5;
    ax2.XColor     = C_TEXT;
    ax2.YColor     = C_TEXT;
    grid(ax2, 'on');
    xlim(ax2, [0.3, n_feats + 0.7]);
    ylabel(ax2, 'Z-Score  (σ units)', 'FontSize', 11, 'Color', C_TEXT, 'FontWeight', 'bold');
    title(ax2, {'After Z-Score Standardisation'; 'All features on the same scale  (μ=0, σ=1)'}, ...
          'FontSize', 12, 'Color', C_TEXT, 'FontWeight', 'bold');
    lgd2 = legend(ax2, 'Location', 'northeast', 'FontSize', 8);
    lgd2.Color     = C_BG;
    lgd2.EdgeColor = [0.80 0.70 0.60];
    lgd2.TextColor = C_TEXT;
    hold(ax2, 'off');

    % ══════════════════════════════════════════════════════════════════════
    % SUBPLOT 3 — Standard deviation comparison (grouped bar)
    % ══════════════════════════════════════════════════════════════════════
    ax3 = subplot(2, 2, 3);
    set(ax3, 'Color', C_BG);
    hold(ax3, 'on');

    bar_data = [raw_std(:), z_std(:)];
    b = bar(ax3, bar_data, 'grouped');
    b(1).FaceColor    = C_RAW;
    b(1).FaceAlpha    = 0.80;
    b(1).EdgeColor    = 'none';
    b(1).DisplayName  = 'Raw std  (σ_raw)';
    b(2).FaceColor    = C_NORM;
    b(2).FaceAlpha    = 0.80;
    b(2).EdgeColor    = 'none';
    b(2).DisplayName  = 'Z-score std  (σ_z ≈ 1)';

    % Reference line at σ = 1
    plot(ax3, [0.4, n_feats+0.6], [1, 1], '--', ...
         'Color', [C_ZERO 0.8], 'LineWidth', 1.5, ...
         'DisplayName', 'Target σ = 1');

    ax3.XTick      = 1:n_feats;
    ax3.XTickLabel = feat_names;
    ax3.XTickLabelRotation = 35;
    ax3.FontSize   = 9;
    ax3.Color      = C_BG;
    ax3.GridColor  = C_GRID;
    ax3.GridAlpha  = 0.5;
    ax3.XColor     = C_TEXT;
    ax3.YColor     = C_TEXT;
    grid(ax3, 'on');
    xlim(ax3, [0.4, n_feats + 0.6]);
    ylabel(ax3, 'Standard Deviation (σ)', 'FontSize', 11, 'Color', C_TEXT, 'FontWeight', 'bold');
    title(ax3, {'Standard Deviation Before vs After'; 'Raw σ varies wildly — Z-score collapses to 1'}, ...
          'FontSize', 12, 'Color', C_TEXT, 'FontWeight', 'bold');
    lgd3 = legend(ax3, 'Location', 'northeast', 'FontSize', 8);
    lgd3.Color     = C_BG;
    lgd3.EdgeColor = [0.80 0.70 0.60];
    lgd3.TextColor = C_TEXT;
    hold(ax3, 'off');

    % ══════════════════════════════════════════════════════════════════════
    % SUBPLOT 4 — Feature range table (text-based, clean)
    % ══════════════════════════════════════════════════════════════════════
    ax4 = subplot(2, 2, 4);
    set(ax4, 'Color', C_BG, 'XColor', C_BG, 'YColor', C_BG);
    axis(ax4, 'off');
    hold(ax4, 'on');

    title(ax4, {'Feature Statistics: Before vs After  z = (x − μ) / σ'; ''}, ...
          'FontSize', 12, 'Color', C_TEXT, 'FontWeight', 'bold');

    % Column headers
    col_hdrs = {'Feature', 'Raw Min', 'Raw Max', 'Raw σ', 'Raw μ', ...
                'z Min', 'z Max', 'z σ'};
    col_x    = [0.00, 0.18, 0.30, 0.42, 0.54, 0.66, 0.78, 0.90];
    row_h    = 1.0 / (n_feats + 2);

    % Header row
    for c = 1:length(col_hdrs)
        text(ax4, col_x(c), 1 - row_h * 0.5, col_hdrs{c}, ...
             'FontSize', 8.5, 'FontWeight', 'bold', 'Color', C_TEXT, ...
             'Units', 'normalized', 'Interpreter', 'none');
    end

    % Separator line
    annotation('line', ...
               [ax4.Position(1), ax4.Position(1)+ax4.Position(3)], ...
               [ax4.Position(2)+ax4.Position(4)*0.88, ...
                ax4.Position(2)+ax4.Position(4)*0.88], ...
               'Color', [0.78 0.13 0.31], 'LineWidth', 1.5);

    % Data rows
    for f = 1:n_feats
        row_y = 1 - row_h * (f + 0.5);
        bg_col = C_BOX_RAW;
        if mod(f,2)==0, bg_col = C_BOX_NRM; end

        % Alternating row background
        annotation('rectangle', ...
                   [ax4.Position(1), ...
                    ax4.Position(2) + ax4.Position(4)*row_y - 0.005, ...
                    ax4.Position(3), ...
                    row_h*ax4.Position(4) + 0.003], ...
                   'FaceColor', bg_col, 'FaceAlpha', 0.18, ...
                   'EdgeColor', 'none');

        vals = {feat_names{f}, ...
                sprintf('%.3f', raw_min(f)), ...
                sprintf('%.3f', raw_max(f)), ...
                sprintf('%.3f', raw_std(f)), ...
                sprintf('%.3f', raw_mean(f)), ...
                sprintf('%.3f', z_min(f)), ...
                sprintf('%.3f', z_max(f)), ...
                sprintf('%.3f', z_std(f))};

        for c = 1:length(vals)
            fc = C_TEXT;
            fw = 'normal';
            if c == 1,                  fc = [0.08 0.30 0.08]; fw = 'bold'; end
            if c >= 6,                  fc = [0.55 0.08 0.20]; end
            if c == 8 && z_std(f) > 0.99 && z_std(f) < 1.01
                fw = 'bold';            % highlight σ≈1
            end
            text(ax4, col_x(c), row_y, vals{c}, ...
                 'FontSize', 8, 'Color', fc, 'FontWeight', fw, ...
                 'Units', 'normalized', 'Interpreter', 'none');
        end
    end

    % Footer note
    text(ax4, 0.00, -0.04, ...
         'Green cols = raw  ·  Rose cols = z-score  ·  σ_z ≈ 1.000 confirms correct standardisation', ...
         'FontSize', 7.5, 'Color', [0.55 0.40 0.35], ...
         'Units', 'normalized', 'Interpreter', 'none');
    hold(ax4, 'off');

    % ══════════════════════════════════════════════════════════════════════
    % Global title + annotation
    % ══════════════════════════════════════════════════════════════════════
    sgtitle({'Melodix — Feature Normalisation: Before vs After Z-Score Standardisation'; ...
             'z = (x − μ) / σ   ensures fair contribution of all features to similarity measures'}, ...
            'FontSize', 14, 'FontWeight', 'bold', 'Color', C_TEXT);

    annotation('textbox', [0.01 0.01 0.98 0.03], ...
               'String', { ...
                   ['LA Concepts:  Matrix column-wise mean (μ)  ·  Standard deviation (σ)  ·  ' ...
                    'Element-wise subtraction & division  ·  Prevents feature dominance in dot products']}, ...
               'FitBoxToText', 'on', 'EdgeColor', [0.85 0.75 0.65], ...
               'BackgroundColor', [0.98 0.95 0.89], ...
               'FontSize', 8, 'Color', [0.45 0.25 0.20], ...
               'HorizontalAlignment', 'center');

    % ── Save ─────────────────────────────────────────────────────────────
    saveas(fig, '../data/graph2_normalisation_comparison.png');
    fprintf('[Graph 2] Saved → data/graph2_normalisation_comparison.png\n');
end