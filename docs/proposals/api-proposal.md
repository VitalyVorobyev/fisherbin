В целом текущий API мне нравится. Самое важное решение уже правильное: **`optimize_partition()` и `fit_quantizer()` должны оставаться двумя разными top-level operations**. Сейчас это не искусственное разделение API, а точное отражение двух разных математических задач.

Но до условного `1.0` я бы всё-таки сделал несколько изменений. Причём два из них считаю достаточно существенными.

### 1. Добавить явную схему score space — это для меня главный пробел

Сейчас `ProfiledDOptimality` идентифицирует parameters of interest как

```python
sq.ProfiledDOptimality(interest=(4,))
```

то есть через индексы колонок.

Для toy example это нормально. Для реального HEP case с десятками компонент — уже довольно опасно. Пользователь должен помнить, что column 37 означает конкретный parameter, что reference component удалён, что ordering нигде не поменялся и т. д.

Я бы ввёл что-то вроде:

```python
schema = sq.ScoreSchema(
    parameters=["T", "B", "monocyte", "mast", "HSPC"],
    reference_point=[...],
)

scores = sq.ScoreSample(
    values,
    weights,
    schema=schema,
    provenance=...,
)
```

Тогда:

```python
criterion = sq.ProfiledDOptimality(
    interest=["HSPC"],
)
```

или, если хочется сохранить criterion полностью независимым от schema:

```python
criterion = sq.ProfiledDOptimality(
    interest=schema.select("HSPC"),
)
```

Я бы предпочёл первый вариант.

Важно, что **schema и provenance — разные вещи**. Сейчас `ScoreProvenance` хорошо отвечает на вопрос *«откуда эти scores появились?»*: exact, autodiff, estimated ratio и т. д.  `ScoreSchema` должен отвечать на другой вопрос: *«что означает каждая координата?»*

Это дало бы ещё и гораздо лучшие reports:

```text
interest: HSPC
nuisance: T, B, monocyte, mast
```

вместо `(4,)`.

Для меня это **P0 перед стабильным API**.

---

### 2. `ScoreSample` должен быть canonical input для обеих задач

Сейчас имеется небольшая асимметрия:

```python
sq.optimize_partition(
    scores,
    weights=weights,
    provenance=provenance,
    ...
)
```

но:

```python
sq.fit_quantizer(
    sq.ScoreSample(scores, weights, provenance=provenance),
    ...
)
```

То есть библиотека уже имеет хороший объект **weighted score law**, но одна из двух основных функций его не принимает.

Я бы сделал:

```python
sample = sq.ScoreSample(
    scores,
    weights,
    schema=schema,
    provenance=provenance,
)

partition = sq.optimize_partition(sample, n_bins=8)
quantizer = sq.fit_quantizer(sample, n_bins=8)
```

и оставил array shorthand:

```python
sq.optimize_partition(scores, weights=weights, n_bins=8)
```

для простых случаев.

Тогда mental model становится чрезвычайно чистым:

```text
ScoreSample
   ├── optimize_partition()  → finite labels
   └── fit_quantizer()       → reusable rule
```

При этом я **не стал бы** разрешать

```python
optimize_partition(ObservationSample(...), provider=...)
```

потому что нынешнее требование явно вызвать `provider.score(X)` хорошо подчёркивает границу fixed-sample task.

---

### 3. Я бы переименовал `score=` в `provider=` или `score_provider=`

Сейчас:

```python
sq.fit_quantizer(
    observations,
    score=classifier_score,
)
```

но аргумент `score` на самом деле не score array и не score function обязательно, а **ScoreProvider object**. Более того, `ScoreSample` этот аргумент запрещает.

После нашей сегодняшней систематизации это особенно бросается в глаза.

Я бы предпочёл:

```python
sq.fit_quantizer(
    sample,
    provider=classifier_score,
    ...
)
```

или более явно:

```python
score_provider=classifier_score
```

`provider=` мне нравится больше: коротко и уже есть ясный тип.

---

### 4. `ScoreProvider` стоит сделать настоящим публичным Protocol

Сейчас `ScoreProvider` фактически является union:

```python
type ScoreProvider = (
    ScoreFunction
    | LinearComponentScore
    | DensityRatioScore
    | CentralLogRatioScore
)
```

Но концептуально интерфейс удивительно простой:

```python
class ScoreProvider(Protocol):
    provenance: ScoreProvenance

    def score(self, observations) -> ArrayLike:
        ...
```

Именно это я бы и сделал public contract.

Тогда сторонний пользователь сможет написать:

```python
class MyMadMinerScore:
    provenance = ...

    def score(self, events):
        ...
```

без необходимости оборачивать всё в `ScoreFunction`.

Built-ins (`DensityRatioScore`, `LinearComponentScore`, ...) остаются convenience implementations этого protocol.

Это хорошо соответствует самой архитектуре:

```text
arbitrary statistical machinery
           ↓
      ScoreProvider
           ↓
        ScoreSample
           ↓
       ScoreQuant
```

---

### 5. Разделить **fitted result** и **deployable quantizer**

Это второй более серьёзный архитектурный вопрос.

Сейчас `QuantizerResult` одновременно хранит:

* centers + transform + metric, то есть сам predictor;
* training labels;
* train/validation reports;
* optimization trace;
* provenance;
* criterion и config;
* solver diagnostics.

При этом его `to_dict()` специально говорит:

> not a versioned artifact format.

Для библиотеки, одной из главных целей которой является **получить правило для будущих событий**, я бы хотел иметь очень явный объект:

```python
fit = sq.fit_quantizer(...)

fit.quantizer
```

где

```python
Quantizer
    transform
    centers
    metric
    predict_scores()
```

а всё остальное находится в `QuantizerFit` / `QuantizerResult`.

Например:

```python
fit = sq.fit_quantizer(...)

fit.train_report
fit.validation_report
fit.trace

q = fit.quantizer
bins = q.predict_scores(scores)
```

И обязательно:

```python
q.save("my_quantizer.sq")
q2 = sq.Quantizer.load("my_quantizer.sq")
```

с **versioned serialization contract**.

Это особенно важно, если ScoreQuant становится software product, а не только research implementation.

`PartitionResult.compile_quantizer()` тогда естественно возвращает именно маленький `Quantizer`, а не притворяется новым training result.

---

### 6. Root namespace сейчас перегружен

Сейчас `scorequant.__all__` содержит несколько десятков объектов: workflows, criteria, configs, reports, information utilities, ratio utilities, plotting, certificates, transforms и т. д.

Я бы оставил top level очень удобным для 90% использования:

```python
sq.optimize_partition
sq.fit_quantizer

sq.ScoreSample
sq.ObservationSample

sq.DOptimality
sq.ProfiledDOptimality

sq.DExchangeConfig
sq.SoftVoronoiConfig

sq.ScoreFunction
sq.DensityRatioScore
```

А более специализированное сгруппировал:

```python
sq.information.fisher(...)
sq.information.profiled(...)
sq.diagnostics.exchange_stability(...)
sq.certify.partition(...)
sq.ratios.from_posteriors(...)
sq.plot.summary(...)
```

Не обязательно запрещать старые imports сразу. Но **canonical documented API** я бы сделал более компактным.

Сейчас newcomer видит одновременно `EfficientScoreBound`, `GeometryReport`, `RatioClosureReport`, `FisherTransform`, `fractional_fisher_information` и `fit_quantizer`. Трудно понять, что является core API, а что advanced machinery.

---

### 7. Я бы поправил restart terminology

У `DExchangeConfig` одновременно есть:

```python
n_init=8
n_restarts=1
```

причём `n_init` — количество k-means seeding restarts **внутри** exchange restart, а `n_restarts` — количество самих exchange runs.

Это слишком легко понять неправильно, потому что в sklearn-like API `n_init` обычно означает почти то же, что здесь `n_restarts`.

Я бы использовал что-то вроде:

```python
initializer_restarts=8
solver_restarts=1
```

или даже сделал initializer отдельным:

```python
DExchangeConfig(
    initializer=KMeansInit(n_restarts=8),
    n_restarts=1,
)
```

Второе архитектурно красивее, но может быть избыточно.

---

## Как выглядел бы мой ideal public API

Не радикально иначе, чем сейчас:

```python
import scorequant as sq

scores = sq.ScoreSample(
    values,
    weights,
    schema=sq.ScoreSchema(
        parameters=["T", "B", "monocyte", "mast", "HSPC"],
        reference_point=theta0,
    ),
    provenance=sq.ScoreProvenance(kind="estimated_ratio"),
)

# Task 1: this finite sample
partition = sq.optimize_partition(
    scores,
    n_bins=8,
    criterion=sq.DOptimality(),
)

# Task 2: reusable rule
fit = sq.fit_quantizer(
    scores,
    n_bins=8,
    criterion=sq.ProfiledDOptimality(
        interest=["HSPC"],
    ),
    config=sq.SoftVoronoiConfig(),
)

quantizer = fit.quantizer
future_bins = quantizer.predict_scores(future_scores)

quantizer.save("flowcyt-8bins.sq")
```

И observation-space route:

```python
provider = sq.DensityRatioScore.from_classifier(
    classifier.predict_proba,
    class_priors,
    sq.MixtureParameterization(theta0),
)

fit = sq.fit_quantizer(
    sq.ObservationSample(events, weights),
    provider=provider,
    n_bins=8,
    criterion=sq.DOptimality(),
)
```

Это почти ваша нынешняя архитектура. То есть я **не вижу необходимости переделывать API с нуля**. Я вижу необходимость сделать уже хорошую структуру более явно выраженной.

Если расставить приоритеты перед API freeze, я бы сделал: **(1) named score schema → (2) `ScoreSample` как shared canonical input → (3) `provider=` → (4) отдельный serializable `Quantizer` artifact → (5) public `ScoreProvider` protocol**. Остальное можно менять позже.
