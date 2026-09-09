---
version: alpha
name: RiskAssess Bot · НЛМК
colors:
  primary: "#008fff"          # primary-blue-500 (accent-500) — фирменный синий НЛМК
  primaryDark: "#167ffb"       # primary-blue-600 (accent-600)
  navy900: "#112542"
  navy800: "#0b3461"
  ink900: "#001729"
  ink700: "#4d5d69"
  ink600: "#66747e"
  ink400: "#99a2a9"
  paper: "#ffffff"
  canvas: "#edeeef"
  line: "#e5e8ea"
  spectrumGreen10: "#e5f8e8"
  spectrumGreen60: "#0d932b"
  spectrumRed10: "#ffedf0"
  spectrumRed60: "#ee1505"
  spectrumYellow10: "#ffffe6"
  spectrumOrange60: "#f97b0f"
  spectrumSky10: "#dff7fe"
  spectrumSky60: "#0096e2"
typography:
  heading1: { fontFamily: "Golos Text, PT Root UI, Segoe UI, Arial, sans-serif", fontSize: 48px, fontWeight: 800, lineHeight: 56px }
  heading2: { fontFamily: "Golos Text, PT Root UI, Segoe UI, Arial, sans-serif", fontSize: 32px, fontWeight: 800, lineHeight: 40px }
  heading3: { fontFamily: "Golos Text, PT Root UI, Segoe UI, Arial, sans-serif", fontSize: 24px, fontWeight: 800, lineHeight: 32px }
  heading4: { fontFamily: "Golos Text, PT Root UI, Segoe UI, Arial, sans-serif", fontSize: 20px, fontWeight: 800, lineHeight: 28px }
  subheading1: { fontFamily: "Golos Text, PT Root UI, Segoe UI, Arial, sans-serif", fontSize: 32px, fontWeight: 400, lineHeight: 40px }
  subheading2: { fontFamily: "Golos Text, PT Root UI, Segoe UI, Arial, sans-serif", fontSize: 24px, fontWeight: 400, lineHeight: 32px }
  body: { fontFamily: "Golos Text, PT Root UI, Segoe UI, Arial, sans-serif", fontSize: 18px, fontWeight: 400, lineHeight: 28px }
  body1: { fontFamily: "Golos Text, PT Root UI, Segoe UI, Arial, sans-serif", fontSize: 16px, fontWeight: 400, lineHeight: 24px }
  body2: { fontFamily: "Golos Text, PT Root UI, Segoe UI, Arial, sans-serif", fontSize: 14px, fontWeight: 400, lineHeight: 20px }
  caption: { fontFamily: "Golos Text, PT Root UI, Segoe UI, Arial, sans-serif", fontSize: 12px, fontWeight: 400, lineHeight: 16px }
  mono: { fontFamily: "IBM Plex Mono, SFMono-Regular, monospace", fontSize: 13px, fontWeight: 700, lineHeight: 18px }
spacing:
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 24px
rounded:
  chip: 4px
  card: 8px
  pill: 16px
components:
  alert:
    padding: 12px
    gap: 8px
    minHeight: 48px
    rounded: 4px
    success: { backgroundColor: "#e5f8e8", textColor: "#0d932b" }
    error: { backgroundColor: "#ffedf0", textColor: "#ee1505" }
    warning: { backgroundColor: "#ffffe6", textColor: "#f97b0f" }
    info: { backgroundColor: "#dff7fe", textColor: "#0096e2" }
  badge:
    padding: "3px 9px"
    rounded: 4px
    fontSize: 11.5px
    fontWeight: 700
  card:
    backgroundColor: "#ffffff"
    borderColor: "#e5e8ea"
    rounded: 8px
  sidebar:
    backgroundColor: "#112542"
    collapsedWidth: 74px
    expandedWidth: 250px
---

## Overview

RiskAssess Bot — интерфейс риск-менеджмента для мегапроекта НЛМК (Программа
ЦГП-2), реализованный на Streamlit. Визуальный язык — прямое применение
дизайн-системы **НЛМК ds-2.0** (github.com/nlmk-group/ds-2.0): токены цвета
и типографики взяты из компонентов `Colors`, `Typography` и `Alert` этого
репозитория и живого стенда ds.nlmk.com. Формат этого файла соответствует
спецификации DESIGN.md (github.com/google-labs-code/design.md) — YAML
front-matter с токенами + прозаические секции ниже.

## Colors

Основной цвет бренда — `primary` (#008FFF, `primary-blue-500`), используется
для активной навигации, кнопок, ссылок и акцентных элементов. Тёмно-синий
`navy900` — фон бокового меню. Текст — оттенки `ink` (900→400, от заголовков
к второстепенному тексту). Фон приложения — нейтральный `canvas` (#EDEEEF),
карточки — `paper` (белый) с тонкой границей `line`.

Статусные/severity-цвета следуют паттерну ds-2.0 **Alert**: у каждого цвета
два уровня — `-10` (очень светлый фон-подложка) и `-60` (насыщенный текст).
Это не декоративный выбор — так устроен реальный компонент Alert в ds-2.0
(`Alert.module.scss`), и все статус-пилюли, бейджи категорий и нативные
предупреждения Streamlit (`st.error/warning/success/info`) в этом проекте
перекрашены под этот же паттерн, а не оставлены на дефолтных цветах
Streamlit.

Тёмная тема инвертирует нейтральные тона (canvas/paper/line/ink), сохраняя
`primary` и severity-цвета без изменений — как и в исходном HTML-прототипе.

## Typography

Шрифт — `Golos Text` (с фолбэком на `PT Root UI` — оригинальный шрифт
ds-2.0, недоступный как веб-шрифт вне корпоративной сети). Шкала заголовков
и текста воспроизводит реальные размеры компонента `Typography` ds-2.0
(`Typography.module.scss`: `heading1-48` … `caption-12`): H1 48/56,
H2 32/40, H3 24/32, H4 20/28, Subheading1 32/40 (Regular), Subheading2
24/32 (Regular), Body 18/28, Body1 16/24, Body2 14/20, Caption 12/16.
Моноширинный `IBM Plex Mono` — для ID рисков, чисел, дат и score-значений
(табличные цифры).

## Layout

Максимальная ширина контента — 1280px, боковая панель фиксированной высоты.
Карточки/панели — `st.container(border=True)`, переопределённый под
токены card (белый фон, граница `line`, radius 8px). Сетка риск-матрицы —
3 колонки × 3 строки (P×I), с ячейками фиксированного размера и лёгким
цветовым тоном по severity (`-10`/`-50` фон).

## Elevation & Depth

Тени используются экономно: карточка входа/профиля — мягкая тень
`0 20px 50px -20px rgba(0,23,41,.25)`, всплывающий toast —
`0 8px 24px -8px rgba(0,23,41,.3)`. Обычные панели — без тени, только
граница `line`, что соответствует плоскому, «инженерному» характеру ds-2.0
(в отличие от объёмных Material-подобных теней).

## Shapes

Радиусы: `chip` 4px — для бейджей/пилюль/алертов (как в реальном
`Alert.module.scss`, `border-radius: 4px`), `card` 8px — для панелей и
кнопок, `pill` 16px — только там, где нужна полностью скруглённая форма
(например, счётчик уведомлений). Прямые углы избегаются везде, кроме
таблиц.

## Components

- **Alert** — светлый фон severity-10 + текст severity-60, radius 4px,
  padding 12px, gap 8px, min-height 48px. Применён к `st.error`,
  `st.warning`, `st.success`, `st.info` через переопределение
  `div[data-testid="stAlertContainer"]` (Streamlit по умолчанию красит их
  в свои цвета — это исправлено).
- **Badge/Pill** — те же severity-токены, radius 4px, используются для
  категорий риска, статусов процесса и статусов мероприятий.
- **Score-pill** — единственное исключение из паттерна «светлый фон +
  тёмный текст»: заливка сплошным цветом + белый текст, специально для
  визуального выделения числового score в таблицах и матрице.
- **Sidebar** — тёмно-синий (`navy900`), в свёрнутом состоянии показывает
  только иконки (74px), при наведении раскрывается до 250px с подписями
  (чистый CSS `:hover`, без перезагрузки страницы и без потери сессии).
- **Card/Panel** — нативный `st.container(border=True)` Streamlit,
  переопределённый под токены card.

## Do's and Don'ts

- **Делай:** используй пары `-10`/`-60` для любого нового статуса или
  категории — так visual language остаётся единым с ds-2.0 Alert.
- **Делай:** заголовки — только через реальные теги `h1`–`h4`
  (`st.title`/`st.header`/`st.subheader`/markdown `#`), чтобы шкала
  типографики применялась автоматически.
- **Не делай:** не вводи новые фирменные цвета вне палитры ds-2.0 — если
  нужен ещё один статус, ищи ближайший `spectrum-*` аналог, а не
  придумывай новый hex.
- **Не делай:** не оставляй нативные предупреждения Streamlit неперекра-
  шенными — они не входят в цветовую систему НЛМК из коробки.
