% FILE: visualise.m
% Generates 5 plots for the demo and report.
% =============================================================

function visualise(S, names, final_scores, p1_scores, p1_idx, query_idx, soulmate_matrix, users)

%% ── Plot 1: Top-5 similar songs — bar chart ──────────────────────────────
figure(1);
top_names = names(p1_idx(2:6));    % skip rank 1 (the query itself)
top_scores = p1_scores(2:6);

bar(categorical(top_names), top_scores, 'FaceColor', [0.32 0.29 0.87]);
title(sprintf('Songs similar to "%s" (Pillar 1)', names{query_idx}));
xlabel('Song');
ylabel('Cosine similarity');
ylim([0 1]);
grid on;


%% ── Plot 2: Feature space scatter ────────────────────────────────────────
figure(2);
scatter(S(:,2), S(:,3), 80, final_scores, 'filled');
colorbar;
colormap('cool');
title('Songs in feature space (energy vs danceability)');
xlabel('Energy (normalised)');
ylabel('Danceability (normalised)');

% Label points
for i = 1:length(names)
    text(S(i,2) + 0.01, S(i,3), names{i}, ...
        'FontSize', 6, 'Color', [0.3 0.3 0.3]);
end

% Highlight query song
hold on;
scatter(S(query_idx,2), S(query_idx,3), 150, 'r', 'filled', 'MarkerEdgeColor','k');
text(S(query_idx,2)+0.01, S(query_idx,3), ['◀ ', names{query_idx}], ...
     'FontSize', 8, 'Color', 'red', 'FontWeight', 'bold');
hold off;

grid on;


%% ── Plot 3: Top-5 final recommendations ─────────────────────────────────
figure(3);
[sorted_scores, sorted_idx] = sort(final_scores, 'descend');

% Remove query song
mask = sorted_idx ~= query_idx;
sorted_idx = sorted_idx(mask);
sorted_scores = sorted_scores(mask);

top5_names = names(sorted_idx(1:5));
top5_scores = sorted_scores(1:5);

b = bar(categorical(top5_names), top5_scores, 'FaceColor', [0.18 0.72 0.54]);
title(sprintf('Top-5 Final Recommendations for "%s"', names{query_idx}));
xlabel('Song');
ylabel('Final Score');
ylim([0 1]);
grid on;

% Labels on bars
xtips = b.XEndPoints;
ytips = b.YEndPoints;
labels = string(round(top5_scores * 100, 1)) + "%";
text(xtips, ytips + 0.02, labels, ...
    'HorizontalAlignment','center', 'FontSize', 9);


%% ── Plot 4: Soulmate Heatmap ────────────────────────────────────────────
if nargin >= 7 && ~isempty(soulmate_matrix)
    figure(4);
    imagesc(soulmate_matrix);
    colorbar;
    colormap('hot');
    title('Music Soulmates — User × User Similarity');
    xlabel('User');
    ylabel('User');

    if nargin >= 8 && ~isempty(users) && iscell(users)
        n = length(users);
        xticks(1:n);
        yticks(1:n);
        xticklabels(users);
        yticklabels(users);
        xtickangle(45);
    end

    % Annotate matrix
    n = size(soulmate_matrix, 1);
    for i = 1:n
        for j = 1:n
            text(j, i, sprintf('%.2f', soulmate_matrix(i,j)), ...
                'HorizontalAlignment','center', ...
                'FontSize', 7, 'Color', 'white');
        end
    end
end


%% ── Plot 5: Soulmate bar chart ──────────────────────────────────────────
if nargin >= 7 && ~isempty(soulmate_matrix)
    figure(5);
    n = size(soulmate_matrix, 1);

    % Remove self-match
    S_no_self = soulmate_matrix - 2*eye(n);
    [top_scores_sm, top_idx_sm] = max(S_no_self, [], 2);

    if nargin >= 8 && ~isempty(users) && iscell(users)
        user_labels = users;
        soulmate_labels = users(top_idx_sm);
        x_labels = strcat(user_labels, ' ↔ ', soulmate_labels);
    else
        x_labels = arrayfun(@(i) ...
            sprintf('User%d ↔ User%d', i, top_idx_sm(i)), ...
            1:n, 'UniformOutput', false)';
    end

    bar(categorical(x_labels), top_scores_sm * 100, ...
        'FaceColor', [0.95 0.45 0.25]);
    title('Top Music Soulmate Matches (%)');
    xlabel('Pair');
    ylabel('Match %');
    ylim([0 100]);
    grid on;
    xtickangle(30);
end

end