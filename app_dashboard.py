import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard Sakila",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: #f8f9fa;
    }
    .section-title {
        font-size: 1.3rem;
        font-weight: bold;
        margin-top: 20px;
        color: #f8f9fa;
    }
    .metric-card {
        padding: 12px;
        border-radius: 10px;
        background-color: #1e1e1e;
        color: #ffffff;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
        margin: 5px;
    }
    h1, h2, h3 {
        color: #f8f9fa;
    }
    hr {
        border: 1px solid #444;
    }
    </style>
""", unsafe_allow_html=True)

# --- CARGA DE LOS CSV ---
@st.cache_data
def cargar_csv():
    df_detalle = pd.read_csv("detalle_alquileres_limpio.csv")
    df_alquileres_mes = pd.read_csv("alquileres_por_mes_categoria_limpio.csv")
    df_clientes = pd.read_csv("clientes_mas_frecuentes_limpio.csv")
    df_peliculas = pd.read_csv("peliculas_mas_rentables_limpio.csv")
    df_ingresos = pd.read_csv("ingresos_por_tienda_categoria_limpio.csv")
    return df_detalle, df_alquileres_mes, df_clientes, df_peliculas, df_ingresos

df_detalle, df_alquileres_mes, df_clientes, df_peliculas, df_ingresos = cargar_csv()

# --- TÍTULO ---
st.title("🎬 Dashboard - Análisis de la Base Sakila")
st.markdown("Explora los reportes organizados por pestañas. Selecciona el análisis que deseas visualizar.")

# --- PESTAÑAS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Detalle Alquileres",
    "Alquileres por Mes y Categoría",
    "Clientes Más Frecuentes",
    "Películas Más Rentables",
    "Ingresos por Tienda y Categoría"
])

# --- TAB 1: DETALLE ALQUILERES ---
with tab1:
    st.markdown("<div class='section-title'>🎛️ Análisis de Detalle de Alquileres</div>", unsafe_allow_html=True)
    st.dataframe(df_detalle.head())
    
    # --- KPIs GENERALES ---
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📈 KPIs Generales</div>", unsafe_allow_html=True)

    total_alquileres = df_detalle.shape[0]
    categorias_unicas = df_detalle["categoria"].nunique()

    dias_mas_alquilados = df_detalle['weekday'].value_counts()
    dia_top = dias_mas_alquilados.idxmax()
    cantidad_top = dias_mas_alquilados.max()
    dia_bajo = dias_mas_alquilados.idxmin()
    cantidad_baja = dias_mas_alquilados.min()

    # KPIs como tarjetas
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.markdown(f"<div class='metric-card'><h3>🎬 Total Alquileres</h3><h2>{total_alquileres}</h2></div>", unsafe_allow_html=True)
    kpi2.markdown(f"<div class='metric-card'><h3>📂 Categorías Únicas</h3><h2>{categorias_unicas}</h2></div>", unsafe_allow_html=True)
    kpi3.markdown(f"<div class='metric-card'><h3>📅 Día con más alquileres</h3><h2>{dia_top} ({cantidad_top})</h2></div>", unsafe_allow_html=True)
    kpi4.markdown(f"<div class='metric-card'><h3>📉 Día con menos alquileres</h3><h2>{dia_bajo} ({cantidad_baja})</h2></div>", unsafe_allow_html=True)

    # --- GRÁFICOS ---
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📊✨ Visualizaciones</div>", unsafe_allow_html=True)

    # --- Gráfico de Horas ---
    if 'hour' in df_detalle.columns:
        conteo_horas = df_detalle['hour'].value_counts().sort_index().reset_index()
        conteo_horas.columns = ['Hora', 'Cantidad de Alquileres']

        fig = px.bar(
            conteo_horas, x='Hora', y='Cantidad de Alquileres',
            text='Cantidad de Alquileres', color='Cantidad de Alquileres',
            color_continuous_scale='Viridis',
            title="Frecuencia de Alquileres por Hora del Día",
            template="plotly_dark"
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(xaxis=dict(tickmode='linear'))

    # --- Gráfico de Género ---
    if 'genero_estimado' in df_detalle.columns:
        conteo_genero = df_detalle['genero_estimado'].value_counts().reset_index()
        conteo_genero.columns = ['Género', 'Cantidad']

        fig_genero = px.bar(
            conteo_genero, x='Género', y='Cantidad',
            text='Cantidad', color='Género',
            color_discrete_sequence=px.colors.qualitative.Set2,
            title="Distribución de Alquileres por Género Estimado",
            template="plotly_dark"
        )
        fig_genero.update_traces(texttemplate='%{text}', textposition='outside')

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig, use_container_width=True)
        st.caption("🔍 **Insight:** Las horas pico de alquileres se concentran entre 14:00 y 21:00 horas.")
    with col2:
        st.plotly_chart(fig_genero, use_container_width=True)
        st.caption("🔍 **Insight:** Predomina el género masculino en las estimaciones.")

    # --- Gráfico de Categorías ---
    if 'categoria' in df_detalle.columns:
        conteo_cats = df_detalle.groupby(['categoria', 'genero_estimado']).size().reset_index(name='Cantidad')

        fig_top_cats = px.bar(
            conteo_cats, x='categoria', y='Cantidad',
            color='genero_estimado', barmode='group',
            text='Cantidad', color_discrete_sequence=px.colors.sequential.Magma,
            title="Categorías por Género Estimado",
            template="plotly_dark"
        )
        fig_top_cats.update_traces(texttemplate='%{text}', textposition='outside')
        fig_top_cats.update_layout(
            xaxis_title="Categoría", yaxis_title="Cantidad de Alquileres",
            xaxis_tickangle=-45, legend_title_text='Género',
            legend=dict(x=1.05, y=1, traceorder='normal', orientation='v')
        )

    # --- Gráfico de Días ---
    if 'weekday' in df_detalle.columns:
        conteo_dias = df_detalle['weekday'].value_counts().reindex(
            ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        ).reset_index()
        conteo_dias.columns = ['Día', 'Cantidad']

        fig_dias = px.bar(
            conteo_dias, x='Cantidad', y='Día',
            orientation='h', text='Cantidad', color='Cantidad',
            color_continuous_scale='Plasma',
            title="Alquileres por Día de la Semana",
            template="plotly_dark"
        )
        fig_dias.update_traces(texttemplate='%{text}', textposition='outside')

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(fig_top_cats, use_container_width=True)
        st.caption("🔍 **Insight:** Acción, Animación y Sports dominan el top de categorías.")
    with col4:
        st.plotly_chart(fig_dias, use_container_width=True)
        st.caption("🔍 **Insight:** Los fines de semana muestran mayor actividad, pero se observa un pico de alquileres el día Martes.")


    


   

# --- TAB 2: ALQUILERES POR MES Y CATEGORÍA ---
with tab2:
    st.subheader("📆 Alquileres por Mes y Categoría")
    st.dataframe(df_alquileres_mes.head())
    if 'mes' in df_alquileres_mes.columns:
        fig, ax = plt.subplots(figsize=(8, 4))
        df_alquileres_mes.groupby('mes')["total_alquileres"].sum().plot(ax=ax, marker='o')
        plt.xlabel("Mes")
        plt.ylabel("Total de Alquileres")
        st.pyplot(fig)

# --- TAB 3: CLIENTES MÁS FRECUENTES ---
with tab3:
    st.subheader("👤 Clientes Más Frecuentes")
    st.dataframe(df_clientes.head())

    if 'cliente' in df_clientes.columns and 'total_gasto' in df_clientes.columns:
        top_clientes = df_clientes.set_index('cliente')["total_gasto"].head(10)
        st.bar_chart(top_clientes)

# --- TAB 4: PELÍCULAS MÁS RENTABLES ---
with tab4:
    st.subheader("🎥 Películas Más Rentables")
    st.dataframe(df_peliculas.head())

    if 'pelicula' in df_peliculas.columns and 'ingresos' in df_peliculas.columns:
        top_peliculas = df_peliculas.set_index('pelicula')["ingresos"].head(10)
        st.bar_chart(top_peliculas)

# --- TAB 5: INGRESOS POR TIENDA Y CATEGORÍA ---
with tab5:
    st.subheader("🏬 Ingresos por Tienda y Categoría")
    st.dataframe(df_ingresos.head())

    if {'categoria', 'tienda', 'ingresos'}.issubset(df_ingresos.columns):
        pivot_data = df_ingresos.pivot(index="categoria", columns="tienda", values="ingresos")
        st.bar_chart(pivot_data)
        
        
## para ejecutar el script:  python -m streamlit run app_dashboard.py

