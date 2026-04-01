function [taste_vec, scores, sorted_idx] = pillar2_taste(S, liked_indices)

    num_songs  = size(S, 1);
    scores     = zeros(num_songs, 1);
    sorted_idx = (1:num_songs)';

    if isempty(liked_indices)
        warning('pillar2_taste: liked_indices is empty; returning zero scores.');
        taste_vec = zeros(1, size(S, 2));
        return;
    end

    liked_songs = S(liked_indices, :);
    taste_vec   = mean(liked_songs, 1);

    fprintf('Taste vector: energy=%.2f  dance=%.2f  valence=%.2f  acoustic=%.2f  tempo=%.2f\n', ...
            taste_vec(1), taste_vec(2), taste_vec(3), taste_vec(4), taste_vec(5));

    taste_norm = norm(taste_vec);

    if taste_norm == 0
        warning('pillar2_taste: taste vector has zero norm; returning zero scores.');
        return;
    end

    for i = 1:num_songs
        candidate      = S(i, :);
        candidate_norm = norm(candidate);

        if candidate_norm == 0
            scores(i) = 0;
        else
            scores(i) = dot(taste_vec, candidate) / (taste_norm * candidate_norm);
        end
    end

    [scores, sorted_idx] = sort(scores, 'descend');
end