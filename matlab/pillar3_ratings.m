function [predicted, sorted_idx] = pillar3_ratings(R, user_idx)

    [~, num_songs] = size(R);

    user_row  = R(user_idx, :);
    rated     = user_row(user_row > 0);
    user_mean = mean(rated);

    song_means = zeros(1, num_songs);
    for j = 1:num_songs
        col          = R(:, j);
        rated_values = col(col > 0);
        if ~isempty(rated_values)
            song_means(j) = mean(rated_values);
        end
    end

    predicted = (user_mean + song_means) / 2;

    predicted(user_row > 0) = 0;

    [predicted_sorted, sorted_idx_row] = sort(predicted, 'descend');

    predicted  = predicted_sorted(:);
    sorted_idx = sorted_idx_row(:);
end