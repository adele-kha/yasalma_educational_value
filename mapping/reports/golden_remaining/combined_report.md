# Combined review of the remaining golden references

All **4,265,586 crawl records in 50 shards** were searched. Scope: **171** previously unmatched golden references.

| Evidence category (exclusive) | Golden references |
|---|---:|
| exact_visible | 0 |
| exact_compact_review | 0 |
| page_identity_review | 29 |
| high_lexical_or_contained_review | 0 |
| near_reordered_or_partial_review | 42 |
| url_alias_only_review | 1 |
| weak_only | 39 |
| no_candidate | 60 |

Categories prioritize exact visible text, compact text, page identity, strong lexical evidence, near/partial/reordered text, URL-only evidence, weak overlap, then no candidate. A page identity or lexical candidate does not establish label applicability. No semantic similarity was used.

Belem print/node IDs and current Wikipedia page IDs identify page versions. Current Wikipedia metadata may describe a later revision. URL-only evidence can also be an embedded link or an oEmbed response rather than the source document.

Full texts, original labels and crawl locators are in `data/golden_remaining_v2/candidates.parquet` and `print_url_candidates.parquet`. `review.json` lists evidence for every target. Baseline files and human labels are unchanged; no annotation sample is created.

## Per-reference overview

| Reference ID | Evidence category | Original URL |
|---|---|---|
| 02d1d45b-b214-4eb6-b559-51245232128d | weak_only | http://tnv.ru/tat/main1/novosti/kul_tura/kazan_tormysh_syjfaty_buencha_rossiyane_i_yahshy_shrlre_isemlegend/ |
| 04c990b2-47fc-4961-9273-3d955a15448c | page_identity_review | https://tt.wikipedia.org/wiki/%D0%92%D1%8C%D0%B5%D1%82%D0%BD%D0%B0%D0%BC_%D0%A1%D2%96_%D0%B4%D3%99%D2%AF%D0%BB%D3%99%D1%82_%D2%BB%D0%B8%D0%BC%D0%BD%D1%8B |
| 0566a787-fb93-4e08-b410-3a2c08bd2059 | no_candidate | http://tt.cnkqs.com/news/aseptic-cold-filling-production-line-reached-a-new-cooperation/ |
| 0804a0dd-f1a6-44f7-ba50-a1b9d49a141f | no_candidate | http://tt.burcharry.com/news/the-2022-dalang-sweater-festival-came-to-a-successful-conclusion/ |
| 097d5ef1-16ca-48fa-b971-c46e47b666e1 | weak_only | https://belem.ru/node/2049 |
| 0ae3fe1e-244e-46ec-bf16-07b6b836824d | near_reordered_or_partial_review | https://tt.wikipedia.org/wiki/%D0%9F%D0%BE%D1%80%D1%82%D0%B0%D0%BB:%D0%9A%D0%B0%D0%B9%D0%B1%D1%8B%D1%87_%D1%80%D0%B0%D0%B9%D0%BE%D0%BD%D1%8B |
| 0cbd89d6-ac2e-4cc3-afc3-2031849cce86 | page_identity_review | https://tt.wikipedia.org/wiki/%D0%9C%D0%BE%D0%BD%D0%B3%D0%BE%D0%BB_%D1%80%D0%B0%D1%81%D0%B0%D1%81%D1%8B |
| 0cecdcaf-09b3-4315-9917-9db28882cdc4 | page_identity_review | https://tt.wikipedia.org/wiki/%D0%9A%D0%B5%D1%88%D0%B5_%D1%85%D0%BE%D0%BA%D1%83%D0%BA%D0%BB%D0%B0%D1%80%D1%8B_%D0%B1%D1%83%D0%B5%D0%BD%D1%87%D0%B0_%D0%95%D0%B2%D1%80%D0%BE%D0%BF%D0%B0_%D0%A1%D1%83%D0%B4%D1%8B_%D2%BB%D3%99%D0%BC_%D0%A0%D1%83%D1%81%D0%B8%D1%8F |
| 11a822ff-361b-4e25-8476-bcf6019575a2 | page_identity_review | https://tt.wikipedia.org/wiki/%D0%A0%D1%83%D1%81%D0%B8%D1%8F%D0%B4%D3%99_%D0%B8%D1%81%D0%BB%D0%B0%D0%BC |
| 126e2c81-029e-4872-8c92-d1d07d590835 | no_candidate | https://tt.wikipedia.org/wiki/%D0%9A%D1%83%D0%BB%D0%BB%D0%B0%D0%BD%D1%83%D1%87%D1%8B_%D0%B1%D3%99%D1%85%D3%99%D1%81%D0%B5:%D0%9A%D3%99%D1%80%D0%B8%D0%BC%D0%BE%D0%B2%D0%B0_%D0%A0%D1%83%D0%B7%D0%B8%D1%8F |
| 153934a8-9a97-4630-8504-b253b58e66af | no_candidate | http://idel-tat.ru/kazanda-halykara-sammit-start-aldy/ |
| 15ab184e-1168-427a-bc62-93b1946c1725 | near_reordered_or_partial_review | http://saby-rt.ru/news/novosti/anna-popova-kovidka-karshy-krsht-tatarstanda-ber-minutka-da-khafalanu-bulmady |
| 1632211f-92e2-4954-b11a-f4b86bea556f | no_candidate | https://tt.wikipedia.org/wiki/Википедия_бәхәсе:Тавыш_бирү:Бәйге_кысаларында_булдырылган_мәкаләләрне_викиләштерү#Русский_перевод_текста_правила_Конкурсы@татВП |
| 16e1cbac-c03e-47fa-8a3e-22b003cd4906 | no_candidate | https://tt.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D0%BF%D0%B5%D0%B4%D0%B8%D1%8F:%D0%91%D3%99%D0%B9%D0%B3%D0%B5%D0%BB%D3%99%D1%80/%D0%A4%D0%93%D0%9E%D0%A1.wiki/2022 |
| 1853a473-5dfc-4a7e-863f-050fcccace04 | no_candidate | https://tt.wikipedia.org/wiki/%D0%9A%D0%B0%D0%BB%D1%8B%D0%BF:%D0%91%D0%B0%D1%88_%D0%B1%D0%B8%D1%82/%D0%92%D0%B0%D0%BA%D1%8B%D0%B9%D0%B3%D0%B0%D0%BB%D0%B0%D1%80/2_%D0%B0%D0%B2%D0%B3%D1%83%D1%81%D1%82 |
| 18f62b63-73ff-44f9-a627-fb639160d996 | near_reordered_or_partial_review | https://tt.wikipedia.org/wiki/%D0%9A%D0%B0%D0%BB%D1%8B%D0%BF:%D0%91%D0%B0%D1%88%D0%B1%D0%B8%D1%82/%D0%AF%D1%85%D1%88%D1%8B_%D0%BC%D3%99%D0%BA%D0%B0%D0%BB%D3%99 |
| 1b3fe653-b143-4fef-b98a-87f30f3376ab | near_reordered_or_partial_review | https://darelfonyn.kpfu.ru/kazan-marafony-chydamlyka-tiksher/ |
| 1fcc910e-0697-4c27-a6fa-9f6dfb9fefd1 | page_identity_review | https://tt.wikipedia.org/wiki/%D0%90%D0%B1%D0%B4%D1%83%D0%BB%D0%BB%D0%B0_%D0%94%D3%99%D2%AF%D0%BB%D3%99%D1%82%D1%88%D0%B8%D0%BD |
| 20067d70-dc0a-4c38-a396-37894530c38a | near_reordered_or_partial_review | https://tatar-inform.tatar/news/society/05-05-2020/r-st-m-mi-nehanov-berenche-ukytuchysyn-75-yashlek-yubilee-bel-n-kotlady-5740589 |
| 2194c318-6bc2-4bf2-97dd-61cc5db2862d | no_candidate | http://tt.ndcarbide.com/tungsten-carbide-bearing-bush-product/ |
| 240d36ec-0f12-420d-bbe4-921cbcd3f53f | weak_only | http://tnv.ru/tat/main1/novosti/kul_tura/kazanga_krsh_m_bilbauly_krsh_buencha_dnya_chempionatynda_400_dn_artyk_sportchy_kilchk/ |
| 27f65464-8c6b-4cce-b1a4-c0ba52d10773 | weak_only | https://belem.ru/node/7995 |
| 288f9df9-3ad2-4640-9d22-018033e0d459 | weak_only | https://belem.ru/node/6577 |
| 2ba6227a-fc9f-457a-9f85-3c1fbaa99bd9 | no_candidate | https://tt.wikipedia.org/wiki/%D0%9A%D1%83%D0%BB%D0%BB%D0%B0%D0%BD%D1%83%D1%87%D1%8B_%D0%B1%D3%99%D1%85%D3%99%D1%81%D0%B5:Kuramsha |
| 2c317bea-3b69-44e8-bb60-96a3c241b9bf | near_reordered_or_partial_review | https://belem.ru/node/8327 |
| 2d290f7a-da5a-4eec-8cce-493c1618bf0a | no_candidate | https://tt.wikipedia.org/wiki/%D2%96%D3%99%D0%BB%D0%B8%D0%BB_%D1%87%D0%B0%D1%82%D0%BA%D1%8B%D0%BB%D0%B0%D1%80%D1%8B |
| 2e1743f7-2e1c-4422-9528-a3baaec409e3 | no_candidate | https://tt.videochat.date/%D0%B1%D0%B5%D0%BB%D3%99%D0%BD-%D1%82%D0%B0%D0%BD%D1%8B%D1%88%D1%83-%D0%BF%D0%BE%D0%B4%D0%BA%D0%B0%D1%81%D1%82-%D0%BD%D0%B5%D0%BC%D0%B5%D1%86-%D0%B1%D1%83%D1%88%D0%BB%D0%B0%D0%B9-%D0%BF%D0%BE%D0%B4 |
| 2e662427-af64-48d4-87fd-87e24a4847ff | page_identity_review | https://tt.wikipedia.org/wiki/%D0%91%D0%B0%D1%88%D0%BA%D0%BE%D1%80%D1%82_%D0%B2%D0%BE%D1%81%D1%81%D1%82%D0%B0%D0%BD%D0%B8%D0%B5%D1%81%D0%B5_(1755%E2%80%941756) |
| 2e902e84-2f90-43e2-8d24-98dd1dcbd206 | near_reordered_or_partial_review | https://tt.wikipedia.org/wiki/%D0%A1%D0%B5%D1%80%D0%B3%D0%B5%D0%B9_%D0%A1%D0%BE%D0%BB%D0%BE%D0%B2%D1%8C%D1%91%D0%B2 |
| 2eaf8753-8a5b-448e-8c05-2d268a7ac380 | weak_only | https://www.azatliq.org/z/574/2019/6/12 |
| 2ee14ffe-bac4-45b7-8ced-570849b35ccd | near_reordered_or_partial_review | https://pestrecy-rt.ru/news/jemgiyat/tashkabak-m-solydan-koymak |
| 2f1d9e4f-edeb-497a-b740-060aa4dabc1d | near_reordered_or_partial_review | http://belem.ru/node/5363 |
| 3151675c-556c-486a-b48a-1f324bd97349 | near_reordered_or_partial_review | http://arskmedia.ru/news/faydaly-kishlr/buynnar-avyrtkannan-borych-mae-bulysha |
| 3204c414-c69a-4798-9fb9-b7cd7c61444a | no_candidate | https://belem.ru/node/862 |
| 36133a42-f2fa-4472-a4e8-87f6274050f5 | page_identity_review | https://tt.wikipedia.org/wiki/%D0%9F%D0%BE%D0%BB%D1%8F%D1%80%D0%BB%D0%B0%D1%88%D1%83 |
| 366df05c-0fdc-44b4-9e32-9643617cbaa8 | page_identity_review | http://tt.wikipedia.org/wiki/%D0%9A%D1%8B%D1%80%D1%8B%D0%BC_%D1%82%D0%B0%D1%82%D0%B0%D1%80%D0%BB%D0%B0%D1%80%D1%8B_%D0%B4%D0%B5%D0%BF%D0%BE%D1%80%D1%82%D0%B0%D1%86%D0%B8%D1%8F%D1%81%D0%B5 |
| 375ece21-fd2b-42e2-b172-05896a869196 | weak_only | https://belem.ru/node/8386 |
| 383ec89e-b1ec-4219-96f4-ca587cd0be4f | weak_only | https://obrnadzor.tatarstan.ru/index.htm/news/1997447.htm |
| 3b090173-4707-4522-99f1-f007053030ec | weak_only | http://tat.e-islam.ru/news/?id=119 |
| 3c02b8ac-cb68-4b6a-a7a3-69d5503d8263 | no_candidate | http://tat.e-nkama.ru/news/746/78685/ |
| 3c9ad6f8-3904-458e-80dd-586e20375b53 | near_reordered_or_partial_review | https://tatar-inform.tatar/news/tatar_world/10-10-2019/tubyl-sh-rend-tatar-balalar-lider-m-kt-be-uzachak-5613074 |
| 3d7a50a8-538a-44e0-a230-afc5cb3309a8 | page_identity_review | https://belem.ru/node/6447 |
| 3dc9034f-0387-4786-9b57-0c75914a4ec1 | page_identity_review | https://tt.wikipedia.org/wiki/%D0%91%D0%B5%D1%80%D0%B5%D0%BD%D1%87%D0%B5_%D0%A0%D3%99%D1%81%D3%99%D0%B9_%D0%B8%D0%BD%D0%BA%D1%8B%D0%B9%D0%BB%D0%B0%D0%B1%D1%8B |
| 40346bff-af64-498a-a2ee-6f2628e90db1 | near_reordered_or_partial_review | https://darelfonyn.kpfu.ru/galim-hatyjp-mi-negulovny-kazanyshlar-isemlegen-tagyn-ber-medal-st-lde/ |
| 4332d3da-c184-450f-9916-3c9c718c8bf3 | near_reordered_or_partial_review | https://tatar-inform.tatar/news/culture/15-10-2019/tel-nche-tamak-halyk-teatry-yazuchylar-berlege-r-isene-piesasyn-s-hn-l-shterde-5613802 |
| 4390bea2-998e-4c55-ae83-6649e0e10c64 | page_identity_review | https://tt.wikipedia.org/wiki/%D0%9A%D1%83%D3%99%D1%82_(%D0%B9%D0%BE%D0%BB%D0%B4%D1%8B%D0%B7_%D1%81%D1%83%D0%B3%D1%8B%D1%88%D0%BB%D0%B0%D1%80%D1%8B) |
| 44d6fb78-a927-4440-b4a2-073ba27f57da | page_identity_review | https://tt.wikipedia.org/wiki/%D0%A2%D0%B0%D1%82%D0%B0%D1%80_%D0%B4%D3%99%D2%AF%D0%BB%D3%99%D1%82%D1%87%D0%B5%D0%BB%D0%B5%D0%B3%D0%B5 |
| 47f89a3c-593d-492e-beec-a666be626781 | weak_only | http://tokaevo.ucoz.ru/news/14_08_15_m_dr_s_d_lagerny_ikenche_smenasy_t_mamlandy/2015-08-14-1583 |
| 4823b4c8-5a27-4544-9da7-2d3db8889594 | weak_only | https://agryz-rt.ru/news/yashaesh/sinoptiklar-yagyr-yashenle-yagyr-m-kchle-il-turynda-kist |
| 49495275-0df2-45a1-b7ff-d4cabab6c36f | weak_only | https://tt.wikipedia.org/wiki/%D0%9F%D0%BE%D1%80%D1%82%D0%B0%D0%BB:%D0%97%D0%BE%D0%BE%D0%BB%D0%BE%D0%B3%D0%B8%D1%8F |
| 49f12e4d-5ea0-49fc-9412-9fc7c545c40c | no_candidate | https://tt.wikipedia.org/wiki/%D0%9A%D1%8B%D1%80%D0%B3%D1%8B%D0%B7_(%D0%BC%D3%99%D0%B3%D1%8A%D0%BD%D3%99%D0%BB%D3%99%D1%80) |
| 4a894391-bd93-4f56-9d61-a958c5c74f8c | near_reordered_or_partial_review | https://belem.ru/comment/1169 |
| 4d7cfbba-10f9-410c-aa38-c734ff5007db | weak_only | https://tt.wikipedia.org/wiki/%D0%9F%D1%80%D0%BE%D0%BA%D0%B0%D1%80%D0%B8%D0%BE%D1%82%D0%BB%D0%B0%D1%80 |
| 4da678f2-4e7a-4fda-8e30-e16a2901d72e | no_candidate | https://tt.wikipedia.org/wiki/%D0%9A%D0%B0%D0%BB%D1%8B%D0%BF:%D0%91%D0%B0%D1%88%D0%B1%D0%B8%D1%82/%D0%A1%D0%B0%D0%B9%D0%BB%D0%B0%D0%BD%D0%B3%D0%B0%D0%BD_%D0%BC%D3%99%D0%BA%D0%B0%D0%BB%D3%99 |
| 4e4f8fb7-a65a-4077-8922-2952dafee66c | no_candidate | https://belem.ru/node/746 |
| 4e98723c-e605-4daf-ad4a-57caf03918fe | no_candidate | https://belem.ru/node/2380 |
| 4fba619e-4c26-41e7-a461-c0b53111c82d | weak_only | https://bugulma-tatarstan.ru/news/madaniat/respublikada-etnografik-m-mdni-tanyip-bel-turizmyi |
| 514a5af5-4985-4d3f-b4d2-6ffcdd0bab7a | near_reordered_or_partial_review | https://tt.wikipedia.org/wiki/%D0%A2%D1%80%D0%B8%D1%85%D0%BE%D0%BC%D0%BE%D0%BD%D0%BE%D0%B7 |
| 51bd7535-1f58-40ff-9238-95a9b51e066a | no_candidate | http://100tatarstan.100tatarstan.ru/news/yaalyklar/tatarstan-tzchelre-tassrny-100-ellygy-elynda-100-knd-khastakhan-tzep-tapshyrdylar |
| 53592d61-3a3b-450f-a11d-a74091296f16 | page_identity_review | https://tt.wikipedia.org/wiki/%D0%A0%D1%83%D1%81_%D1%80%D0%B0%D0%B4%D0%B8%D0%BE%D0%BB%D0%B0%D1%80%D1%8B |
| 595b12cd-83f5-461b-a460-42636f98844b | near_reordered_or_partial_review | http://belem.ru/node/7107 |
| 59877a4d-f455-4611-9e8f-05dfe9cf2cd8 | no_candidate | https://tt.wikipedia.org/wiki/%D0%A1%D0%B5%D0%BB%D0%B8%D0%B2%D1%91%D1%80%D1%81%D1%82_%D0%92%D0%B0%D1%81%D0%B8%D0%BB%D1%8C%D0%B5%D0%B2%D0%B8%D1%87_%D0%94%D0%B0%D0%B2%D1%8B%D0%B4%D0%BE%D0%B2_%D0%B8%D1%81%D0%B5%D0%BC%D0%B5%D0%BD_%D0%BC%D3%99%D2%A3%D0%B3%D0%B5%D0%BB%D3%99%D1%88%D1%82%D0%B5%D1%80%D2%AF |
| 59da2696-a4a5-494a-94fe-a84974fa774d | weak_only | http://belem.ru/node/7236 |
| 5b6fbac0-12df-4c81-b289-288b16aec409 | weak_only | https://syuyumbike.ru/news/yanalyklar/tatarstanda-ava-toryshy-nacharlanu-sbple-balalarny-massaklm-kayadyr-alyp-baru-tyela |
| 5e9ce248-f4d9-4431-9366-64491949eafe | near_reordered_or_partial_review | https://belem.ru/node/4593 |
| 60a5a801-8daa-4ef8-bee6-c53b829e27f3 | weak_only | https://giylem.tatar/archives/tag/%D0%BE%D0%BF%D1%82%D0%B8%D0%BA%D0%B0 |
| 60ced986-5812-4f3a-b9f6-55ec7332c884 | no_candidate | http://tt.hzbxgas.com/news/moroccan-customer-visited-the-factory/ |
| 623ccec9-5979-4bd7-a0d4-db888fd3b7e8 | no_candidate | https://tt.wikipedia.org/wiki/%D0%9A%D1%83%D0%BB%D0%BB%D0%B0%D0%BD%D1%83%D1%87%D1%8B_%D0%B1%D3%99%D1%85%D3%99%D1%81%D0%B5:IlnarSelimcan |
| 62467238-4dc9-48c9-b1ee-8a587fe85df3 | page_identity_review | https://tt.wikipedia.org/wiki/%D0%91%D0%A0_%D0%B0%D1%82%D0%BA%D0%B0%D0%B7%D0%B0%D0%BD%D0%B3%D0%B0%D0%BD_%D0%BC%D3%99%D0%B4%D3%99%D0%BD%D0%B8%D1%8F%D1%82_%D1%85%D0%B5%D0%B7%D0%BC%D3%99%D1%82%D0%BA%D3%99%D1%80%D0%B5 |
| 65db5aea-f5f4-4dc0-ad91-7afdc874999e | no_candidate | http://belem.ru/node/1326 |
| 6766a2e9-d1b0-45a8-9b31-6c51296751ad | page_identity_review | https://tt.wikipedia.org/wiki/%D0%A0%D3%99%D1%81%D3%99%D0%B9_%D0%A4%D0%B5%D0%B4%D0%B5%D1%80%D0%B0%D1%86%D0%B8%D1%8F%D1%81%D0%B5%D0%BD%D0%B5%D2%A3_%D0%B4%D3%99%D2%AF%D0%BB%D3%99%D1%82_%D0%B3%D0%B5%D1%80%D0%B1%D1%8B |
| 6e65cf83-3768-4f5e-88cd-cacc370bfb46 | no_candidate | https://belem.ru/node/949 |
| 6f403f07-bbb8-47ce-b94b-9e5b15e047a0 | page_identity_review | https://tt.wikipedia.org/wiki/%D0%A2%D3%A9%D0%BD%D1%8C%D1%8F%D0%BA_%D0%B2%D0%BE%D0%BA%D0%B7%D0%B0%D0%BB%D1%8B_(%D0%BC%D0%B5%D1%82%D1%80%D0%BE_%D1%81%D1%82%D0%B0%D0%BD%D1%86%D0%B8%D1%8F%D1%81%D0%B5) |
| 710f75d8-ec96-4ae9-8e2e-aaeb0b58d16f | no_candidate | http://tt.newlights.com/led-smd-bulb-gu10-mr16-series-product/ |
| 734ecb5a-0b14-478b-a7ee-222bf80f80d4 | page_identity_review | http://belem.ru/node/5446 |
| 7384f899-a6c4-4915-a073-26abe9cca6b2 | weak_only | https://tatar-inform.tatar/news/incident/16-05-2021/kazanda-175nche-gimnaziyad-ge-fa-igag-b-yle-r-vesht-moshenniklyk-ochraklary-eshaygan-5823393 |
| 74edd1db-ed4a-4cb5-bab2-11a793da2cea | near_reordered_or_partial_review | http://nashcheremshan.ru/news/belep-toryigyiz/ktelmgn-boryilyish-ilsya-bdretdinovaga-kiyag-chyig |
| 7752f2b1-f3dc-4c8a-b66f-5e5d042335eb | no_candidate | https://belem.ru/node/2 |
| 77d6e260-b8a0-46e5-88ae-4ba087f1bc88 | no_candidate | http://specpromsnab-u.ru/viewtopic.php?f=10&t=63886 |
| 7a276369-c454-43a1-9650-7b832648f204 | no_candidate | https://tt.wikipedia.org/wiki/%D0%91%D3%99%D1%85%D3%99%D1%81:%D0%A3%D1%82%D0%B5%D1%85%D1%82 |
| 7ea01008-7a35-4ea7-8517-3204f31d7de9 | no_candidate | https://tt.videochat.life/%D1%82%D0%B0%D0%BD%D1%8B%D1%88%D1%83-%D2%BB%D3%99%D0%BC-%D1%87%D0%B0%D1%82-1-%D0%BA%D0%B0%D1%80%D1%82%D0%B0-%D0%BA%D0%B5%D1%80%D2%AF-%D0%B1%D1%83%D1%88%D0%BB%D0%B0%D0%B9-%D2%BB%D3%99%D0%BC-%D1%82%D0%B5%D1%80%D0%BA%D3%99%D0%BB%D0%BC%D0%B8%D1%87%D3%99 |
| 7f9edbb5-8844-4959-8c31-2b7cc8914524 | weak_only | http://idel-tat.ru/news/novosti-tt/musa-barlyk-krshchelrne-yaavyl-saban-tuena-chakyra |
| 83ad1485-02e6-40b6-bdf6-22958f301e4c | no_candidate | https://tt.wikipedia.org/wiki/%D0%91%D3%99%D1%85%D3%99%D1%81:%D2%96%D3%99%D0%BD%D0%B3%D0%B0%D0%BD_(%D0%A1%D0%B0%D0%BB%D1%8C%D1%8F%D0%BD) |
| 85657093-bc91-46f2-9d52-a17997600356 | weak_only | http://belem.ru/node/3752 |
| 858a8be4-e464-4153-87c9-bd066c82f352 | page_identity_review | https://tt.wikipedia.org/wiki/Vasiliy_Molodtsov |
| 86e6e32c-bd20-494f-be9a-fe30a2e7540a | weak_only | http://belem.ru/node/6430 |
| 881fbfa5-ff4f-4e9c-a0a4-f3affb401fe5 | no_candidate | http://tt.wikipedia.org/wiki/%D0%9E%D0%BB%D0%B5%D0%B3_%D0%9A%D2%AF%D1%80%D3%99%D0%B7%D3%99 |
| 8a3bbdd4-0fd1-4916-89f1-536e12dfc78e | no_candidate | http://belem.ru/node/2053 |
| 8ae7a4e1-110d-451f-8d71-4cc45cb19a95 | near_reordered_or_partial_review | https://tt.wikipedia.org/wiki/%D0%A5%D3%99%D0%B4%D0%B8%D1%87%D3%99 |
| 8d5500b9-f7b0-459e-b091-3b024e6ca936 | page_identity_review | http://belem.ru/node/6500 |
| 8e0ef36d-7450-4000-b44d-4e2f55039040 | weak_only | http://yashel-uzan.ru/news/yash%D3%99esh/rossiya-gidrometeorologiya-zgend-yne-i-esse-knnre-turynda-syldelr |
| 911df417-1900-4949-8c91-e190742775e9 | near_reordered_or_partial_review | https://belem.ru/node/2911 |
| 934a5851-c61a-44e7-b508-b751fe2c01a0 | no_candidate | https://tt.wikipedia.org/wiki/%D0%9A%D0%B0%D0%BB%D1%8B%D0%BF:%D0%91%D0%B0%D1%88_%D0%B1%D0%B8%D1%82/%D0%92%D0%B0%D0%BA%D1%8B%D0%B9%D0%B3%D0%B0%D0%BB%D0%B0%D1%80/4_%D0%B0%D0%BF%D1%80%D0%B5%D0%BB%D1%8C |
| 96f15e59-5c0b-4722-bb1f-5bdd13bb6dfb | near_reordered_or_partial_review | http://syuyumbike.ru/yanalyklar/?id=8646 |
| 98890eae-ece1-40df-8ff2-8d032c2a7b02 | near_reordered_or_partial_review | https://yashel-uzan.ru/news/yash%D3%99esh/tatarstanda-pandemiya-arkasynda-darular-falsifikatlary-ylneshe-artkan |
| 99651953-7a24-44c4-9424-d69fe199ba47 | no_candidate | https://tt.wikipedia.org/wiki/%D2%96%D3%99%D0%B1%D3%99%D0%BB%D0%B8%D1%8F |
| 9984aaf6-78a6-4dde-8c09-2c3d43bd6ea6 | weak_only | https://tt.wikipedia.org/wiki/%D0%90%D0%BC%D0%B0%D0%BD%D0%B0%D1%82 |
| 9c3b58b6-268b-4d1a-afba-d68235cf3617 | near_reordered_or_partial_review | https://darelfonyn.kpfu.ru/rossiya-m-garif-ministry-olga-vasileva-tatarstanda-yash-p-telne-belm-bik-k-d-res-t-gel/ |
| 9ce2f9b3-2786-4902-8013-12ce20a8d3ab | no_candidate | https://tt.wikipedia.org/wiki/%D0%9A%D0%B0%D0%BB%D1%8B%D0%BF:Ifempty |
| 9dc9f7ca-abc0-41bc-a456-f2bb21746bb3 | weak_only | https://belem.ru/node/4905 |
| 9ed56cfb-af0f-4a9b-82f0-c4b728797e64 | no_candidate | http://dores.tatar/page/nokta |
| 9fb54635-2e76-425d-9ca5-e112d9387d94 | weak_only | http://yashel-uzan.ru/news/yash%EF%BF%BD%EF%BF%BD%EF%BF%BD%EF%BF%BD%EF%BF%BD%EF%BF%BDesh/olyi-yake-sentelre-yashel-zn-bazaryin-yaulyiy |
| a075e4aa-23d6-427f-a85e-25e160ac0746 | no_candidate | http://tt.decorzoneco.com/news/guide-to-choose-metal-garden-furniture/ |
| a47faa4c-c165-4405-8b3d-3e1dce299ad5 | weak_only | https://tt.wikipedia.org/wiki/%D0%9F%D1%80%D0%BE%D0%B5%D0%BA%D1%82:%D0%A2%D3%A9%D1%80%D0%BA%D0%B8_%D0%BC%D0%B0%D1%80%D0%B0%D1%84%D0%BE%D0%BD/2020 |
| a5d374d0-02fe-402a-bdb2-f239dea69e72 | near_reordered_or_partial_review | https://magarif-uku.ru/tt/tatar-tele-olimpiadasynda-katnashuchy/ |
| a666e761-9180-4293-825c-adc16fb3faa7 | page_identity_review | https://tt.wikipedia.org/wiki/%D0%98%D1%81%D0%BA%D0%B5_%D0%A2%D3%99%D1%80%D0%B1%D0%B8%D1%82_%D0%BC%D3%99%D0%BA%D1%82%D3%99%D0%B1%D0%B5_%D1%82%D0%B0%D1%80%D0%B8%D1%85%D1%8B |
| a6d99dba-3318-4926-8e79-7cd77691be72 | no_candidate | https://educontest.net/ru/1686753/%D0%BC%D0%B8%D0%BD%D0%B5%D0%BC-%D0%BF%D0%B5%D0%B4%D0%B0%D0%B3%D0%BE%D0%B3%D0%B8%D0%BA-%D0%BE%D1%81%D1%82%D0%B0%D0%BB%D1%8B%D0%B3%D1%8B%D0%BC-2016/ |
| a96f04cc-969b-4043-a680-a9f087c866b7 | no_candidate | http://tt.vdbbq.com/grill-brush-scraper-extra-strong-bbq-cleaner-safe-wire-bristles-18-stainless-steel-triple-scrubber-cleaning-brush-product/ |
| aa61bf17-0bbb-48fe-af1d-dc35557dfef4 | no_candidate | http://belem.ru/node/429 |
| ad50b04c-5a1e-4ad4-a10c-2a849087c2f0 | no_candidate | https://tt.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D0%BF%D0%B5%D0%B4%D0%B8%D1%8F:Terk%C3%A4l%C3%BC |
| adfca3c8-aa98-41c4-aa12-ea66899e534e | no_candidate | https://xn----7sbcaucqbthgyg0d8d5c.xn--p1ai/tt/nashi-meropriyatiya/igrovaya-programma-soyuz-dushi-s-dushoy-rodnoy-0 |
| b1e6233b-f7fe-40a8-ae0b-e11fefe73d75 | page_identity_review | https://tt.wikipedia.org/wiki/%D0%91%D0%B0%D1%88%D0%BA%D0%BE%D1%80%D1%82_%D0%B1%D0%B0%D1%88_%D0%BA%D2%AF%D1%82%D3%99%D1%80%D2%AF%D0%BB%D3%99%D1%80%D0%B5_(1735-1740) |
| b270650a-dacc-4da9-8369-06b291de0526 | page_identity_review | https://tt.wikipedia.org/wiki/%D0%A4%D1%80%D0%B0%D0%BD%D1%81%D0%B0 |
| b2fd9cdb-f12c-4a76-8234-8c15986470c5 | no_candidate | https://tt.videochat.world/%D0%B1%D0%B5%D0%BB%D3%99%D0%BD-%D0%BE%D1%87%D1%80%D0%B0%D1%88%D1%83-%D2%BB%D3%99%D0%BC-%D2%97%D0%B8%D1%82%D0%B4%D0%B8-%D0%BC%D3%A9%D0%BD%D3%99%D1%81%D3%99%D0%B1%D3%99%D1%82%D0%BB%D3%99%D1%80-%D3%A9%D1%87%D0%B5%D0%BD-%D0%BA%D1%8B%D0%B7%D0%BB%D0%B0%D1%80-%D1%82%D0%B0%D0%B1%D0%B0%D1%81%D0%BA%D0%BE |
| b3a55cee-3c93-47e9-b81c-38e600b80db4 | weak_only | https://tt.wikipedia.org/wiki/%D0%91%D0%BE%D0%B5%D1%80%D0%B3%D0%B0%D0%BD_%D1%82%D0%B8%D0%BC%D0%B5%D1%80_%D1%8E%D0%BB_%D1%80%D0%B0%D0%B7%D1%8A%D0%B5%D0%B7%D0%B4%D1%8B_%D0%BF%D0%BE%D1%81%D0%B5%D0%BB%D0%BE%D0%B3%D1%8B |
| b4ce8f77-ed75-47e7-81d3-8f89fe9b547d | near_reordered_or_partial_review | https://arskmedia.ru/news/yaalyklar/mikroavtobus-belan-kilep-cykkan-kotockyc-iul-halakatenda-16-kese-ulgan |
| b6770bf9-749b-42a3-b019-f68b09d301c4 | page_identity_review | https://tt.wikipedia.org/wiki/%D0%A2%D0%B0%D1%82%D0%B0%D1%80_%D1%85%D0%B0%D0%BB%D0%BA%D1%8B |
| b716962d-79b2-4aab-bb7a-8e5bfd93e785 | no_candidate | http://belem.ru/node/7224 |
| b8e2ee43-7092-481b-a354-7665d3a7f51b | weak_only | http://tnv.ru/tat/main1/novosti/kul_tura/frit_mhmmtshin_kazanda_balalar_tehnik_iaty_respublikaklm_festivalen_achty/ |
| b948521b-56fa-49c0-8dc5-84d64e5219d0 | weak_only | https://tt.wikipedia.org/wiki/%D0%A4%D0%B0%D1%82%D0%B8%D1%85_%D0%9A%D1%83%D1%82%D0%BB%D1%83 |
| bb41378e-7522-4193-994d-cc353ce126f3 | no_candidate | http://tt.yzrindustry.com/about-us/ |
| bd45a7e2-c2d4-452f-a58a-40365626afc9 | no_candidate | https://simpleoffline.website/kazino-bushlay-chip.html |
| be70cd71-ad87-4c5f-a5b6-523ea1af7852 | no_candidate | https://tt.wikipedia.org/wiki/%D0%AF%D0%BC%D0%BD%D0%BE%D0%B5 |
| bf045855-bbe2-4467-a4f8-89ef3da9f358 | no_candidate | https://belem.ru/node/1378 |
| c1276f33-1054-43a4-ab60-9ed6bbaeb83c | no_candidate | http://tt.yingnuode.com/about-us/ |
| c272781b-29f0-4cbb-ace7-d75fb29ff9b4 | page_identity_review | https://belem.ru/node/4512 |
| c27adb10-7306-4920-b55f-f2a24b6aaed4 | no_candidate | https://belem.ru/node/1141 |
| c342d2a4-741a-4aba-b2c1-87e0819707ee | no_candidate | https://tt.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D0%BF%D0%B5%D0%B4%D0%B8%D1%8F:%D0%9A%D1%8B%D0%B7%D1%8B%D0%BA%D0%BB%D1%8B_%D1%84%D0%B0%D0%BA%D1%82%D0%BA%D0%B0_%D0%BA%D0%B0%D0%BD%D0%B4%D0%B8%D0%B4%D0%B0%D1%82%D0%BB%D0%B0%D1%80 |
| c38dc80f-8d63-400d-b4e4-46d334719fab | near_reordered_or_partial_review | https://belem.ru/node/603 |
| c43d23c9-5249-41f9-b5cd-f99f103c65bd | url_alias_only_review | https://vatantat.ru/2022/11/97781/ |
| c6420137-764d-4021-862a-91b0371df4c1 | page_identity_review | http://belem.ru/node/6182 |
| c76824f7-2cb4-4fcb-bdce-5d0f869a5328 | near_reordered_or_partial_review | https://belem.ru/node/7966 |
| ca223d84-1f23-47bd-b688-53cafe267293 | no_candidate | https://belem.ru/node/3557 |
| ccb5fef6-98a6-4c4b-846a-e380999fed0a | no_candidate | http://belem.ru/node/167 |
| ced8a528-ed62-4c92-83c9-70a06c4674d5 | near_reordered_or_partial_review | https://darelfonyn.kpfu.ru/kfu-galimen-orbeli-isemend-ge-premiya-tapshyryldy/ |
| cf3e508e-cf89-4d17-86a9-88c6fe9490d1 | weak_only | https://saba-rt.ru/news/radio-ham-tv-yanalilari/tatarstanda-tlek-echend-100dn-artyk-keshe-covid-19-beln-zararlangan |
| d01313c0-3335-4d3b-a583-aba9210232cf | near_reordered_or_partial_review | https://tt.wikipedia.org/wiki/%D0%9A%D0%B0%D0%BB%D1%8B%D0%BF:%D0%91%D0%B0%D1%88_%D0%B1%D0%B8%D1%82/%D0%A1%D0%B0%D0%B9%D0%BB%D0%B0%D0%BD%D0%B3%D0%B0%D0%BD_%D0%BC%D3%99%D0%BA%D0%B0%D0%BB%D3%99 |
| d1d3ea37-0e18-4305-8f70-f52b97961497 | weak_only | http://tinchurinteatr.ru/?p=11432 |
| d26cac40-fd36-4431-b4c4-6fdcdaed74eb | weak_only | http://tat.e-nkama.ru/news/746/76617/ |
| d39ce16f-050c-4b71-a1c0-a5148278554d | weak_only | https://belem.ru/node/8630 |
| d4103f19-bbd3-4e33-be0a-a3875185f207 | near_reordered_or_partial_review | https://belem.ru/node/1841 |
| d4e77ce5-a9e4-49e9-8d8c-58d43a10f04d | near_reordered_or_partial_review | https://tt.lawyers.cafe/%D2%97%D0%B0%D0%B2%D0%B0%D0%BF%D0%BB%D0%B0%D1%80-%D1%8E%D1%80%D0%B8%D1%81%D1%82%D0%BB%D0%B0%D1%80-%D0%BE%D0%BD%D0%BB%D0%B0%D0%B9%D0%BD-%D0%B1%D1%83%D1%88%D0%BB%D0%B0%D0%B9 |
| d5e7297a-bd81-464b-85ee-6d35062125b7 | near_reordered_or_partial_review | https://tatar-inform.tatar/news/official/05-05-2016/tr-h-k-m-te-yortynda-kazanda-rossiya-studentlar-yazy-finalyn-tk-r-turynda-s-z-buldy-5263098 |
| d6013f85-c486-4a1d-abcb-87df643b64dc | weak_only | http://belem.ru/node/5843 |
| d770876e-0306-4996-aeea-ac8b3f5c05d9 | page_identity_review | https://tt.wikipedia.org/wiki/%D0%A7%D1%83%D0%BB%D0%BF%D0%B0%D0%BD_%D0%A1%D0%B0%D0%B4%D1%8B%D0%B9%D0%BA%D0%BE%D0%B2%D0%B0 |
| d77ff89c-e630-43b9-a31b-e193af4079d6 | no_candidate | https://tt.wikipedia.org/wiki/%D0%A1%D0%BE%D0%BA%D0%BE%D0%BB_(%D0%BC%D3%99%D0%B3%D1%8A%D0%BD%D3%99%D0%BB%D3%99%D1%80) |
| d7ec9905-00a5-451d-91ad-f3150a285280 | near_reordered_or_partial_review | https://belem.ru/node/8498 |
| d953f595-fc50-47f6-843d-bbdea6f6002c | weak_only | https://tt.wikipedia.org/wiki/%D0%AF%D2%A3%D0%B0_%D0%AE%D0%BB |
| d97ee40b-50cb-4a10-81f8-14a222769ecf | near_reordered_or_partial_review | http://belem.ru/node/6844 |
| d9f5198b-a273-42d6-9267-8ba3c3fe61a1 | no_candidate | https://belem.ru/node/777 |
| da67f910-f439-4cf3-852b-ed1c13067ef6 | weak_only | https://magarif-uku.ru/tt/yakynlashyp-kil%D2%AFche-yana-el-bayrame-belan/ |
| daab6378-f94b-46e8-bab3-b2731ae2d654 | no_candidate | https://tt.roypowtech.com/lifepo4-forklift-batteries-page/ |
| daabef29-8b58-49cf-aab0-d67616eb05a6 | near_reordered_or_partial_review | http://tt.wikipedia.org/wiki/%D0%9F%D0%BE%D1%80%D1%82%D0%B0%D0%BB:%D0%91%D0%B8%D0%BE%D0%BB%D0%BE%D0%B3%D0%B8%D1%8F |
| e3348512-25e2-418f-8407-8bc9884ef5a2 | weak_only | https://tt.wikipedia.org/wiki/%D0%9F%D0%BE%D1%80%D1%82%D0%B0%D0%BB:%D0%A8%D3%99%D1%85%D0%B5%D1%81%D0%BB%D3%99%D1%80 |
| e550f8ef-1fe5-446b-a076-398bcb001dfc | page_identity_review | https://tt.wikipedia.org/wiki/Elvira_N%C3%A4biullina |
| e61e94ae-e13a-4fdb-9676-7dd2e89ca348 | weak_only | http://syuyumbike.ru/news/brendlar/elvin-grey-vsil-fttakhovany-quottugan-yakquot-yryn-bashkarmayachak |
| e88f9793-5146-41ad-9da9-c5e256526e8e | near_reordered_or_partial_review | https://edudocs.info/prezentaciya-na-temu-balyk-bistm-tugan-yagym.html |
| ebcb6c44-218b-4f85-a6a5-24ed5586c242 | near_reordered_or_partial_review | https://tatar-inform.tatar/news/incident/16-11-2020/putin-covid-19-s-b-ple-rossiyad-narkotiklar-kontrabandasy-kimede-5785962 |
| ec36ec08-fa89-4383-a761-293003b62a47 | weak_only | http://tatarlarsamara.org/index.php?id=40&page=3 |
| ecbed885-df23-4840-84e7-6f2df64912db | near_reordered_or_partial_review | https://tt.wikipedia.org/wiki/%D0%9A%D0%B0%D0%BB%D1%8B%D0%BF:%D0%91%D0%B0%D1%88%D0%B1%D0%B8%D1%82/%D0%A1%D0%B0%D0%B9%D0%BB%D0%B0%D0%BD%D0%B3%D0%B0%D0%BD_%D0%BC%D3%99%D0%BA%D0%B0%D0%BB%D3%99 |
| eef5257f-a888-48bb-a471-9cb0277626b2 | near_reordered_or_partial_review | https://belem.ru/node/7105 |
| ef908fba-fad3-43b8-b958-acd9563a3422 | no_candidate | http://simpleoffline.website/kazino-i-yahshi-aktrisa-nominaciyase.html |
| f42f3196-e37e-4828-a964-15c4a88b6038 | no_candidate | https://tt.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D0%BF%D0%B5%D0%B4%D0%B8%D1%8F:%D0%9A%D1%8B%D0%B7%D1%8B%D0%BA%D1%81%D1%8B%D0%BD%D1%83_%D0%BA%D0%BE%D0%BD%D1%84%D0%BB%D0%B8%D0%BA%D1%82%D1%8B |
| f5a0f8f0-71d0-4a41-a704-fdfc1d77af5b | near_reordered_or_partial_review | http://kazanutlary.ru/news/yanaliklar/kazanda-chiklersez-radio-halykara-festivale-bashlandy |
| f62abce3-a112-47b9-be21-cc0745b5d672 | no_candidate | https://tt.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D0%BF%D0%B5%D0%B4%D0%B8%D1%8F:%D0%92%D0%B8%D0%BA%D0%B8-%D0%BA%D0%BB%D1%83%D0%B1 |
| f63ed7a3-9483-4192-a930-e7ac2c9f2bf0 | page_identity_review | https://tt.wikipedia.org/wiki/%D0%97%D0%B0%D1%8F%D1%82%D2%AF%D0%BB%D3%99%D0%BA_%D0%B1%D0%B5%D0%BB%D3%99%D0%BD_%D0%A1%D1%83%D1%81%D1%8B%D0%BB%D1%83 |
| f669ae6d-40a4-4e21-99a2-17837bd4e5f9 | near_reordered_or_partial_review | http://tulachi.ru/news/glavnyie-novosti/balalarga-posobie-bilgel-kagyydlrend-zgreshlr |
| f77b0a88-5952-481e-9b7d-d4adce93b03a | page_identity_review | https://tt.wikipedia.org/wiki/%D0%93%D0%B0%D0%BC%D0%B8%D1%80_%D0%B8%D0%B1%D0%BD%D0%B5_%D2%96%D3%99%D1%80%D1%80%D0%B0%D1%85 |
| fa35b953-3da7-4ed5-ac84-1c83f2920317 | near_reordered_or_partial_review | https://belem.ru/node/6510 |
| ff014422-d254-48bf-8eb6-28cc49b9d7e0 | no_candidate | https://belem.ru/node/774 |
| ff54dba2-54a2-4c74-a083-195cfdd0a232 | no_candidate | https://tt.wikipedia.org/wiki/%D0%92%D0%B8%D0%BA%D0%B8%D0%BF%D0%B5%D0%B4%D0%B8%D1%8F_%D0%B1%D3%99%D1%85%D3%99%D1%81%D0%B5:%D0%AE%D0%90%D0%A8/%D0%9C%D3%A9%D1%80%D3%99%D2%97%D3%99%D0%B3%D0%B0%D1%82%D1%8C%D0%BB%D3%99%D1%80 |
