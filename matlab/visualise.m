% FILE: visualise.m
% Generates 3 plots for the demo and report.
% ═══════════════════════════════════════════════════════════════════════
function visualise(S, names, final_scores, p1_scores, p1_idx, query_idx)
 
    % ── Plot 1: Top-5 similar songs — bar chart ───────────────────────
    figure(1);
    top_names  = names(p1_idx(2:6));       % skip rank 1 (the query itself)
    top_scores = p1_scores(2:6);
 
    bar(categorical(top_names), top_scores, 'FaceColor', [0.32 0.29 0.87]);
    title(sprintf('Songs similar to "%s"  (Pillar 1)', names{query_idx}));
    xlabel('Song');
    ylabel('Cosine similarity');
    ylim([0 1]);
    grid on;
 
    % ── Plot 2: Feature space scatter (energy vs danceability) ────────
    figure(2);
    scatter(S(:,1), S(:,2), 80, final_scores, 'filled');
    colorbar;
    colormap('cool');
    title('Songs in feature space  (energy vs danceability)');
    xlabel('Energy (normalised)');
    ylabel('Danceability (normalised)');
 
    for i = 1:length(names)
        text(S(i,1) + 0.01, S(i,2) + 0.01, names{i}, 'FontSize', 7);
    end
    grid on;
 
    % ── Plot 3: Full similarity matrix — heatmap ──────────────────────
    figure(3);
    norms      = vecnorm(S, 2, 2);         % norm of each row vector
    norm_mat   = norms * norms';            % outer product of all norm pairs
    sim_matrix = (S * S') ./ norm_mat;     % cosine similarity matrix
    sim_matrix = round(sim_matrix, 2);
 
    heatmap(names, names, sim_matrix, ...
            'Title',    'Song similarity matrix  (all vs all)', ...
            'FontSize', 7);
end