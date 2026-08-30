Да. Речь именно о **FlowCyt Classification Benchmark** — датасете из CHIL 2024: 30 пациентов, bone-marrow flow cytometry, примерно 250k–1M клеток на пациента, 14 измеряемых признаков на клетку (в benchmark-коде используются 12), с ground-truth разметкой основных клеточных популяций: T cells, B cells, monocytes, mast cells и HSPCs. ([GitHub][1])

И главное: в контексте ScoreQuant это уже **не просто подходящий внешний датасет, а существующий подробный end-to-end example библиотеки**. Поэтому мою предыдущую таблицу надо исправить.

Я бы теперь считал canonical showcases так:

| Showcase                                | Что именно демонстрирует                                                                                                                              |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **FlowCyt**                             | главный mixture / composition example; реальные пациенты и реальные клетки; sample partition + inductive quantizer; component fractions как параметры |
| **Gaussian / Michelson**                | general parametric inference вне mixture models; analytic score; чистый \(D\) vs \(D_s\)                                                              |
| **HEP direct-score example / MadMiner** | пользователь уже приносит готовые multivariate scores                                                                                                 |
| **HEP classifier example**              | classifier → density ratios → scores → quantizer, включая nuisance parameters                                                                         |

Причём **FlowCyt гораздо сильнее Iris** для нашей библиотеки, и Iris я бы вообще убрал из roadmap основных examples.

FlowCyt особенно хорошо соответствует нашей архитектуре, потому что одна и та же физическая/биологическая задача позволяет показать сразу несколько уровней:

$$
\text{cell observables }x
\rightarrow
\text{cell-population model / classifier}
\rightarrow
\text{density ratios}
\rightarrow
s(x)
\rightarrow
\text{ScoreQuant}.
$$

И есть естественное разделение двух ключевых задач:

* **sample partition:** оптимально разбить клетки конкретного пациента;
* **inductive quantization:** по training patients выучить partition of score space и применять её к клеткам новых пациентов.

Ещё я бы теперь использовал FlowCyt как **основной integration benchmark для разных input interfaces**. Если нынешний пример использует classifier, можно на том же датасете сравнивать:

`precomputed scores`
vs `classifier → ratios → scores`
vs, если мы строим explicit component-density models, `densities/ratios → exact scores`.

Тогда Gaussian/Michelson нужен не как ещё один «красивый датасет», а исключительно чтобы показать важный conceptual point: **ScoreQuant не является mixture-fitting library**.

Так что исправленная иерархия у меня теперь такая: **FlowCyt — существующий flagship non-HEP example**, HEP — flagship application example, Gaussian — minimal general-theory example.

[1]: https://github.com/VIPER-GENEVA/FlowCyt-Classification-Benchmark?utm_source=chatgpt.com "GitHub - VIPER-GENEVA/FlowCyt-Classification-Benchmark: Official repository implementation for \"FlowCyt: A Comparative Study of Deep Learning Approaches for Multi-Class Classification in Flow Cytometry Benchmarking” @CHIL2024 · GitHub"
