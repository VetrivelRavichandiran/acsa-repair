#include <stdio.h>
#include <string.h>

/* Intentionally flawed candidate: its boundary condition permits length == buffer_size. */
int parse_input(const char *input) {
    char payload[16];
    const size_t buffer_size = sizeof(payload);
    const size_t length = strlen(input);

    printf("{\"event_id\":1,\"function\":\"parse_input\",\"location\":{\"file\":\"parser.c\",\"line\":9},\"iteration\":0,\"call_stack\":[\"main\",\"parse_input\"],\"variables\":{\"length\":{\"type\":\"size_t\",\"value\":%zu},\"buffer_size\":{\"type\":\"size_t\",\"value\":%zu}},\"expressions\":{\"length < buffer_size\":%s},\"control_flow\":{\"branch\":\"length_check\"}}\n", length, buffer_size, length < buffer_size ? "true" : "false");
    if (length > buffer_size) {
        printf("{\"event_id\":2,\"function\":\"parse_input\",\"location\":{\"file\":\"parser.c\",\"line\":11},\"iteration\":0,\"call_stack\":[\"main\",\"parse_input\"],\"variables\":{\"length\":{\"type\":\"size_t\",\"value\":%zu},\"buffer_size\":{\"type\":\"size_t\",\"value\":%zu}},\"control_flow\":{\"branch\":\"reject_oversized\"}}\n", length, buffer_size);
        return 0;
    }

    /* Trace only: copying is omitted so this instructional fixture remains safe to run. */
    printf("{\"event_id\":2,\"function\":\"parse_input\",\"location\":{\"file\":\"parser.c\",\"line\":17},\"iteration\":0,\"call_stack\":[\"main\",\"parse_input\"],\"variables\":{\"length\":{\"type\":\"size_t\",\"value\":%zu},\"buffer_size\":{\"type\":\"size_t\",\"value\":%zu}},\"control_flow\":{\"branch\":\"copy_would_overflow\"}}\n", length, buffer_size);
    return 0;
}

int main(int argc, char **argv) {
    return parse_input(argc > 1 ? argv[1] : "safe");
}
