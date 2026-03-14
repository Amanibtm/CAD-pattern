def divider(lengths: list, request: list):
    new_divisions = []

    count_req = 0                  # index of current request
    req_remaining = request[0]     # remaining amount of that request

    for num_length in range(len(lengths)):

        if count_req >= len(request):
            break

        N = lengths[num_length]
        new_divisions.append([])

        while N > 0 and count_req < len(request):

            if req_remaining <= N:
                # consume the rest of the current request
                new_divisions[num_length].append({count_req: req_remaining})
                N -= req_remaining

                count_req += 1
                if count_req < len(request):
                    req_remaining = request[count_req]

            else:
                # partially consume current request
                new_divisions[num_length].append({count_req: N})
                req_remaining -= N
                N = 0

    return new_divisions
