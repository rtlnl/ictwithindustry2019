# EN -> NL translations for 13K ImageNet/WordNet categories

This folder contains all code and data that we used to translate 13K ImageNet categories to Dutch.
We used two general strategies:

1. Leverage the interlingual links between Princeton WordNet and Open Dutch WordNet.
2. If no links exist, use Google Translate to obtain translations for otherwise missing entries.

## Requirements

We used (Anaconda) Python 3.6.6 with the following libraries:

- NLTK 3.3 - to access WordNet
- lxml 4.2.5 - to use the ODWN XML

## Resources

- 30K ImageNet categories from [here](https://staff.fnwi.uva.nl/p.s.m.mettes/codedata.html). Also see Mettes et al. (2016).
- 1K ImageNet categories. See Deng et al. (2009) and Russakovsky et al. (2015).
- Open Dutch WordNet from [here](https://github.com/cltl/OpenDutchWordnet). Also see Postma et al. (2016).
- Places365 data from [here](https://github.com/CSAILVision/places365). Also see Zhou et al. (2018).

## How to reproduce

**30K categories**
1. Run `python wordnet_translate.py`
2. Run `python extract_untranslated.py`
3. Copy `./Output/Incomplete/to_translate.csv` to Google Sheets, and add a column 'translation', with in each column the Google Translate command, e.g. put this in C3: `=GOOGLETRANSLATE(C2,"en","nl")`.
4. Download the file as `./Output/Incomplete/to_translate_sheets.csv`.
5. Run `python combine_translations.py`

Bonus: get English labels for the 13K categories by running:

- `python get_english_labels.py`

**1K categories**
1. Run `python wordnet_translate_1k.py`
2. Copy `./Output/Incomplete/dutch_to_do_1k.tsv` to Google Sheets, and add a column 'translation', with in each column the Google Translate command, e.g. put this in C3: `=GOOGLETRANSLATE(C2,"en","nl")`.
3. Download the file as `./Output/Incomplete/dutch_to_do_1k_sheets.tsv`.
4. Run `python combine_translations.py`

**COCO translation**
1. Upload the categories file to Google sheets, and add a column 'dutch', with in each column the Google Translate command, e.g. put this in B2: `=GOOGLETRANSLATE(A2,"en","nl")`.
2. Download the translations to the resources folder.

**Places365 translations**
1. Run `python places_categories.py`.
2. Upload the fine-grained TSV to Google Sheets, and translate it. Put `=GOOGLETRANSLATE(B2,"en","nl")` in D2, and `=IF(NOT(ISBLANK(C2)),GOOGLETRANSLATE(C2),)` in E2.
3. Download the translations to the resources folder.
4. Manually translate the coarse-grained categories.

## References
- J. Deng, W. Dong, R. Socher, L.-J. Li, K. Li and L. Fei-Fei, ImageNet: A Large-Scale Hierarchical Image Database. IEEE Computer Vision and Pattern Recognition (CVPR), 2009.
- Mettes, Pascal, Dennis C. Koelma, and Cees GM Snoek. "The imagenet shuffle: Reorganized pre-training for video event detection." In Proceedings of the 2016 ACM on International Conference on Multimedia Retrieval, pp. 175-182. ACM, 2016.
- Postma, Marten, Emiel van Miltenburg, Roxane Segers, Anneleen Schoen, and Piek Vossen. "Open Dutch WordNet." In Global WordNet Conference, p. 300. 2016.
- Olga Russakovsky*, Jia Deng*, Hao Su, Jonathan Krause, Sanjeev Satheesh, Sean Ma, Zhiheng Huang, Andrej Karpathy, Aditya Khosla, Michael Bernstein, Alexander C. Berg and Li Fei-Fei. (* = equal contribution) ImageNet Large Scale Visual Recognition Challenge. International Journal of Computer Vision, 2015
- Zhou, Bolei, Agata Lapedriza, Aditya Khosla, Aude Oliva, and Antonio Torralba. "Places: A 10 million image database for scene recognition." IEEE transactions on pattern analysis and machine intelligence 40, no. 6 (2018): 1452-1464.
