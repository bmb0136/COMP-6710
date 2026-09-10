def mann_whitney_u(x, y):
    n1 = len(x)
    n2 = len(y)
    
    # Combine data with group identifiers (0 for x, 1 for y)
    combined = [(val, 0) for val in x] + [(val, 1) for val in y]
    
    # Sort combined data by value
    combined.sort(key=lambda item: item[0])
    
    # Assign ranks, handling ties with average ranks
    n = len(combined)
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j < n and combined[j][0] == combined[i][0]:
            j += 1
        # Calculate average rank for tied values (1-indexed)
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j
        
    # Sum the ranks for the first group (x)
    r1 = sum(ranks[k] for k in range(n) if combined[k][1] == 0)
    
    # Calculate U statistics for both groups
    u1 = n1 * n2 + (n1 * (n1 + 1)) / 2.0 - r1
    u2 = n1 * n2 - u1
    
    return min(u1, u2), u1, u2
