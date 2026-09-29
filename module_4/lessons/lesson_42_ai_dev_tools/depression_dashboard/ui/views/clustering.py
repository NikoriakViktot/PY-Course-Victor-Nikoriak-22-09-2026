import streamlit as st
import pandas as pd
from ui.components.api_client import fetch_clusters
from ui.charts.plotly_charts import cluster_scatter, cluster_radar


def render():
    st.header("🧠 Behavioral Clustering (KMeans + PCA)")

    data = fetch_clusters()

    st.caption(
        f"KMeans · {data['n_clusters']} clusters · "
        f"PCA explains {data['explained_variance']:.1%} of variance"
    )

    st.plotly_chart(cluster_scatter(data), use_container_width=True)

    st.divider()
    st.subheader("Cluster Profiles")

    # урок 42: назви були вшиті в код (0 — «High Pressure», 1 — «Sleep Deprived»…), але номери KMeans
    # довільні: «Sleep Deprived» виявився кластером, що спить найбільше. Назву тепер дає профіль (бекенд).
    profiles = data["cluster_profiles"]
    names = data["cluster_names"]
    sizes = data["cluster_sizes"]
    profile_df = pd.DataFrame(profiles).T
    profile_df.index = [f"Cluster {i} — {names[i]} (n={sizes[i]})" for i in profile_df.index]
    st.dataframe(profile_df.style.format("{:.2f}").background_gradient(cmap="RdYlGn_r"),
                 use_container_width=True)

    st.divider()
    st.subheader("Radar Chart — Cluster Profiles")
    st.plotly_chart(cluster_radar(profiles), use_container_width=True)

    st.divider()
    st.subheader("Cluster Interpretation")
    for cid, label in names.items():
        p = profiles[cid]
        st.write(
            f"**Cluster {cid} — {label}** (n={sizes[cid]}) | Depression rate: {p['Depression']:.1%} | "
            f"Avg Risk Score: {p['Risk_Score']:.2f}"
        )
