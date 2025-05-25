import gradio as gr

# 캐시 교체 정책 구현


def simulate_fifo(
    pages: list[int], cache_size: int
) -> tuple[list[list[int]], list[str]]:
    cache: list[int] = []
    history: list[list[int]] = []
    replaced: list[str] = []
    for p in pages:
        rep = "-"
        if p not in cache:
            if len(cache) >= cache_size:
                rep = str(cache[0])
                cache.pop(0)
            cache.append(p)
        history.append(list(cache))
        replaced.append(rep)
    return history, replaced


def simulate_lru(
    pages: list[int], cache_size: int
) -> tuple[list[list[int]], list[str]]:
    cache: list[int] = []
    history: list[list[int]] = []
    replaced: list[str] = []
    for p in pages:
        rep = "-"
        if p in cache:
            cache.remove(p)
        elif len(cache) >= cache_size:
            rep = str(cache[0])
            cache.pop(0)
        cache.append(p)
        history.append(list(cache))
        replaced.append(rep)
    return history, replaced


def simulate_opt(
    pages: list[int], cache_size: int
) -> tuple[list[list[int]], list[str]]:
    cache: list[int] = []
    history: list[list[int]] = []
    replaced: list[str] = []
    for i, p in enumerate(pages):
        rep = "-"
        if p not in cache:
            if len(cache) < cache_size:
                cache.append(p)
            else:
                # OPT: 앞으로 가장 늦게 쓰일 페이지를 교체
                future = pages[i + 1 :]
                idxs = [
                    (future.index(x) if x in future else float("inf")) for x in cache
                ]
                to_replace = idxs.index(max(idxs))
                rep = str(cache[to_replace])
                cache[to_replace] = p
        history.append(list(cache))
        replaced.append(rep)
    return history, replaced


def format_history(
    history: list[list[int]], replaced: list[str], pages: list[int]
) -> str:
    lines: list[str] = []
    for i, state in enumerate(history):
        rep = replaced[i]
        if rep != "-":
            lines.append(f"Access: {pages[i]}  Cache: {state}  Replaced: {rep}")
        else:
            lines.append(f"Access: {pages[i]}  Cache: {state}")
    return "\n".join(lines)


def format_history_table(
    history: list[list[int]], replaced: list[str], pages: list[int]
) -> list[list[str | int]]:
    table: list[list[str | int]] = []
    for i, state in enumerate(history):
        table.append(
            [
                pages[i],
                ", ".join(map(str, state)),
                replaced[i] if replaced[i] != "-" else "",
            ]
        )
    return table


# Gradio 인터페이스 함수
def cache_simulator(
    pages_str: str, cache_size: int
) -> tuple[list[list[str | int]], list[list[str | int]], list[list[str | int]]]:
    pages = [int(x.strip()) for x in pages_str.split(",") if x.strip()]
    fifo, fifo_rep = simulate_fifo(pages, cache_size)
    lru, lru_rep = simulate_lru(pages, cache_size)
    opt, opt_rep = simulate_opt(pages, cache_size)
    return (
        format_history_table(opt, opt_rep, pages),
        format_history_table(lru, lru_rep, pages),
        format_history_table(fifo, fifo_rep, pages),
    )


with gr.Blocks() as demo:
    gr.Markdown("""
    # 캐시 교체 정책 시뮬레이터
    페이지 참조 시퀀스와 캐시 크기를 입력하면 OPT, LRU, FIFO 정책의 캐시 상태 변화를 표로 보여줍니다.
    """)
    with gr.Row():
        pages_input = gr.Textbox(
            label="페이지 시퀀스 (예: 3,2,1,3,6,3,4,5,6,2,3,2)",
            value="3,2,1,3,6,3,4,5,6,2,3,2",
        )
        cache_size_input = gr.Number(label="캐시 크기", value=3, precision=0)
    with gr.Tab("OPT 결과"):
        opt_out = gr.Dataframe(
            headers=["Access", "Cache", "Replaced"],
            datatype=["number", "str", "str"],
            label="OPT 결과",
        )
    with gr.Tab("LRU 결과"):
        lru_out = gr.Dataframe(
            headers=["Access", "Cache", "Replaced"],
            datatype=["number", "str", "str"],
            label="LRU 결과",
        )
    with gr.Tab("FIFO 결과"):
        fifo_out = gr.Dataframe(
            headers=["Access", "Cache", "Replaced"],
            datatype=["number", "str", "str"],
            label="FIFO 결과",
        )
    run_btn = gr.Button("시뮬레이션 실행")
    run_btn.click(
        cache_simulator,
        inputs=[pages_input, cache_size_input],
        outputs=[opt_out, lru_out, fifo_out],
    )

demo.launch()
