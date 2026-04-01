function [scores, sorted_idx] = pillar1_similarity(S, query_idx)

    query      = S(query_idx, :);
    num_songs  = size(S, 1);
    scores     = zeros(num_songs, 1);
    query_norm = norm(query);

    if query_norm == 0
        warning('pillar1_similarity: query song has zero-norm feature vector.');
        sorted_idx = (1:num_songs)';
        return;
    end

    for i = 1:num_songs
        candidate      = S(i, :);
        candidate_norm = norm(candidate);

        if candidate_norm == 0
            scores(i) = 0;
        else
            scores(i) = dot(query, candidate) / (query_norm * candidate_norm);
        end
    end

    [scores, sorted_idx] = sort(scores, 'descend');
end