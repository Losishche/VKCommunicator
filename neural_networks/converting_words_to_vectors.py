import gensim

w2v_fpath = "all.norm-sz500-w10-cb0-it3-min5.w2v"  # ""all.norm-sz100-w10-cb0-it1-min100.w2v"
w2v = gensim.models.KeyedVectors.load_word2vec_format(w2v_fpath, binary=True, unicode_errors='ignore')
w2v.init_sims(replace=True)

for word, score in w2v.most_similar(positive=[u"король", u"женщина"], negative=[u"мужчина"]):
    print(word, score)
