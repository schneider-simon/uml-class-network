import inflection
import pandas as pd
import networkx as nx


def main():
    key = "xmi_id"
    limit_names = 300

    path = './cd_class.csv'
    output = './network.gexf'
    df = pd.read_csv(path)

    df['slug'] = df.apply(lambda x: sluggify_name(x), axis=1)

    top_names = df['slug'].value_counts().head(limit_names)
    top_names = top_names.drop('empty').drop('')

    df_top = df.loc[df['slug'].isin(top_names.index)]

    df_grouped = df_top.groupby(key)
    graph = nx.Graph()

    i = 0
    for name, group in df_grouped:
        print("Model %s out of %s (%s classes)" % (i, len(df_grouped), len(group)))
        add_model_to_graph(group, graph)
        i += 1

    nx.write_gexf(graph, output)
    print("Wrote result to: %s" % output)


def sluggify_name(row):
    slug = row['cls_name'].split('/')[-1]
    slug = slug.split('\\')[-1]
    pieces = slug.split('.')

    if len(pieces) != 2 or len(pieces[1]) > 4:
        slug = pieces[-1]

    slug = inflection.underscore(slug.strip())
    return slug


def add_model_to_graph(df, graph: nx.Graph):
    if len(df) > 30:
        return

    for i in range(0, len(df) - 1):
        class1 = df.iloc[i]
        upsert_node(class1['slug'], graph)
        graph.nodes[class1['slug']]['size'] += 1

        for j in range(i + 1, len(df) - 1):
            class2 = df.iloc[j]

            if class1['slug'] is class2['slug']:
                continue

            upsert_node(class2['slug'], graph)

            add_weight_to_edge(class1['slug'], class2['slug'], 1, graph)


def add_weight_to_edge(id1, id2, increment, g):
    ids = [id1, id2]
    ids.sort()

    if not g.has_edge(ids[0], ids[1]):
        g.add_edge(ids[0], ids[1], weight=0)

    g[ids[0]][ids[1]]['weight'] += increment

    return g[ids[0]][ids[1]]


def upsert_node(slug: str, g: nx.Graph):
    if g.has_node(slug):
        return g.nodes[slug]

    g.add_node(slug, slug=slug, size=0)

    return g.nodes[slug]


if __name__ == "__main__":
    main()
