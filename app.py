from typing import Dict, List, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from flask import Flask, render_template, request

app = Flask(__name__)

# Gunakan hasil simulasi dari notebook sebagai sumber data utama aplikasi
DATA_PATH = "hasil_simulasi_sampah_bandung.csv"


def load_data() -> pd.DataFrame:
    """Baca dataset simulasi dan pastikan kolom tanggal siap dipakai."""
    df = pd.read_csv(DATA_PATH)
    if "tanggal" in df.columns:
        df["tanggal"] = pd.to_datetime(df["tanggal"])
    else:
        bulan_map = {
            "JANUARI": 1, "FEBRUARI": 2, "MARET": 3, "APRIL": 4,
            "MEI": 5, "JUNI": 6, "JULI": 7, "AGUSTUS": 8,
            "SEPTEMBER": 9, "OKTOBER": 10, "NOVEMBER": 11, "DESEMBER": 12,
        }
        df["bulan_num"] = df["bulan"].str.upper().map(bulan_map)
        df["tanggal"] = pd.to_datetime(
            df["tahun"].astype(str) + "-" + df["bulan_num"].astype(str) + "-01"
        )
    return df.sort_values("tanggal")


def build_summary(df: pd.DataFrame) -> Dict[str, str]:
    total = df["jumlah_sampah"].sum()
    rata_penanganan = df["penanganan_estimasi"].mean()
    sisa_akhir = df["sisa_sampah"].iloc[-1]
    akumulasi_akhir = df["akumulasi"].iloc[-1]
    periode = f"{df['tahun'].min()} - {df['tahun'].max()}"
    return {
        "periode": periode,
        "total_sampah": f"{total:,.0f} ton",
        "total_sampah_value": float(total),
        "rata_penanganan": f"{rata_penanganan:,.0f} ton/bulan",
        "rata_penanganan_value": float(rata_penanganan),
        "sisa_akhir": f"{sisa_akhir:,.0f} ton",
        "sisa_akhir_value": float(sisa_akhir),
        "akumulasi_akhir": f"{akumulasi_akhir:,.0f} ton",
        "akumulasi_akhir_value": float(akumulasi_akhir),
    }


def build_insights(df: pd.DataFrame) -> List[str]:
    highest = df.loc[df["jumlah_sampah"].idxmax()]
    lowest = df.loc[df["jumlah_sampah"].idxmin()]
    best_intervention = df["skn_80"].iloc[-1]
    bau_end = df["skn_BAU"].iloc[-1]
    delta = bau_end - best_intervention
    return [
        f"Puncak timbulan terjadi pada {highest['bulan'].title()} {int(highest['tahun'])} sebesar {highest['jumlah_sampah']:,.0f} ton.",
        f"Periode terendah adalah {lowest['bulan'].title()} {int(lowest['tahun'])} dengan {lowest['jumlah_sampah']:,.0f} ton.",
        f"Skenario 80% menurunkan akumulasi akhir sebesar {delta:,.0f} ton dibanding BAU.",
    ]


def render_plotly(fig: go.Figure) -> str:
    return fig.to_html(full_html=False, include_plotlyjs="cdn", config={"displaylogo": False})


def generate_charts(df: pd.DataFrame) -> Tuple[str, str, str]:
    """Render grafik interaktif Plotly."""
    fig_tren = px.line(
        df,
        x="tanggal",
        y="jumlah_sampah",
        title="Tren Jumlah Sampah Bulanan",
        markers=True,
        labels={"tanggal": "Periode", "jumlah_sampah": "Ton Sampah"},
    )
    fig_tren.update_layout(margin=dict(l=20, r=20, t=60, b=20))

    fig_akumulasi = px.line(
        df,
        x="tanggal",
        y="akumulasi",
        title="Akumulasi Sampah (BAU)",
        markers=True,
        labels={"tanggal": "Periode", "akumulasi": "Ton"},
    )
    fig_akumulasi.update_traces(line_color="#d9534f")
    fig_akumulasi.update_layout(margin=dict(l=20, r=20, t=60, b=20))

    fig_skenario = go.Figure()
    fig_skenario.add_trace(
        go.Scatter(
            x=df["tanggal"],
            y=df["skn_BAU"],
            mode="lines",
            name="BAU (60%)",
            line=dict(dash="dash", color="#6c757d"),
        )
    )
    fig_skenario.add_trace(
        go.Scatter(
            x=df["tanggal"],
            y=df["skn_70"],
            mode="lines+markers",
            name="Skenario 70%",
            line=dict(color="#0d6efd"),
        )
    )
    fig_skenario.add_trace(
        go.Scatter(
            x=df["tanggal"],
            y=df["skn_80"],
            mode="lines+markers",
            name="Skenario 80%",
            line=dict(color="#198754"),
        )
    )
    fig_skenario.update_layout(
        title="Perbandingan Skenario Kebijakan",
        xaxis_title="Periode",
        yaxis_title="Ton",
        margin=dict(l=20, r=20, t=60, b=20),
    )

    return (
        render_plotly(fig_tren),
        render_plotly(fig_akumulasi),
        render_plotly(fig_skenario),
    )


@app.route("/")
def index():
    df = load_data()
    years = sorted(df["tahun"].unique())
    year_from = request.args.get("year_from")
    year_to = request.args.get("year_to")

    df_view = df.copy()
    if year_from and year_from.isdigit():
        df_view = df_view[df_view["tahun"] >= int(year_from)]
    if year_to and year_to.isdigit():
        df_view = df_view[df_view["tahun"] <= int(year_to)]

    if df_view.empty:
        df_view = df.copy()
        year_from = ""
        year_to = ""

    summary = build_summary(df_view)
    insights = build_insights(df_view)
    tren_html, akumulasi_html, skenario_html = generate_charts(df_view)
    table_html = df_view.tail(24).to_html(
        classes="table table-striped table-hover table-sm align-middle",
        index=False,
        table_id="datasetTable",
    )

    return render_template(
        "index.html",
        table=table_html,
        tren=tren_html,
        akumulasi=akumulasi_html,
        skenario=skenario_html,
        summary=summary,
        insights=insights,
        years=years,
        year_from=year_from or "",
        year_to=year_to or "",
    )


if __name__ == "__main__":
    app.run(debug=True)
