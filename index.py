import streamlit as st 
import pyTigerGraph as tg
import spacy

@st.cache(allow_output_mutation=True)
def loadModel():
    return spacy.load("en_core_sci_lg")

@st.cache(allow_output_mutation=True)
def createConnection():
    conn = tg.TigerGraphConnection(host="https://bleve.i.tgcloud.io/", graphname="OurGraph")
    conn.apiToken = conn.getToken(conn.createSecret())
    return conn

nlp = loadModel()
conn = createConnection()
st.title('TigerWikiSearch')
selected = st.text_input("Search for Terms Here!", placeholder="Search...")
button_clicked = st.button("Search")

if (button_clicked):
    search = st.empty()

    print(selected)
    val = search.caption(f"Searching for {selected}...")

    terms = nlp(selected)
    print(terms.ents)

    conn.upsertVertex("Doc", "search_doc", attributes = {"id": "search_doc", "content": "graph"})
    for i in terms.ents:
        conn.upsertEdge("Doc", "search_doc", "DOC_ENTITY", "Entity", str(i))

    res = conn.runInstalledQuery("jaccard_pagerank_score", params = {"source": ("search_doc", "Doc"), "e_type": "DOC_ENTITY", "rev_e_type": "DOC_ENTITY"})

    conn.delVerticesById("Doc", "search_doc")

    val = search.caption(f"Found {len(res[0]['Others'])} results for {selected}!")

    for i in res[0]["Others"]:
        print(f"# ({' '.join(i['v_id'].split('/')[-1].split('_'))})[{i['v_id']}]")
        print(i["attributes"]["content"])
        st.title(f"[{' '.join(i['v_id'].split('/')[-1].split('_')).capitalize()}]({i['v_id']})")
        st.write(' '.join(i["attributes"]["content"].split('\n')))
        print(i["attributes"]["@entities"])
        st.caption('Keywords: ' + ", ".join(["".join(tag.split("\n")) for tag in i["attributes"]["@entities"]]))
