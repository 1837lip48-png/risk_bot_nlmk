# RiskLesson — дизайн-система (сведено из 6 Figma Make экспортов)

## Что общего у всех 6 файлов (можно взять как есть, без споров)

- **Стек:** React + TypeScript + Vite + Tailwind v4 + shadcn/ui + Radix UI + lucide-react — идентичен во всех 6 архивах, это дефолтный экспорт Figma Make.
- **Токены темы** (файл `theme.css`/`globals.css`) — побайтово совпадают во всех 6:
  - `--radius: 0.625rem` (≈10px, из него выводятся `sm/md/lg/xl`)
  - `--primary: #030213` (почти чёрный, не синий — важно, значит их «primary» кнопки чёрные, не брендово-синие)
  - `--border: rgba(0,0,0,0.1)`, `--muted-foreground: #717182`
  - `--destructive: #d4183d`
  - `--chart-1…5`: `oklch(0.646 0.222 41.116)`, `oklch(0.6 0.118 184.704)`, `oklch(0.398 0.07 227.392)`, `oklch(0.828 0.189 84.429)`, `oklch(0.769 0.188 70.08)` — палитра для графиков
  - Есть готовая `.dark` тема (тёмный режим) — тоже одинаковая везде
- **Типографика:** шрифт не переопределён нигде (`fonts.css` пустой во всех проектах) → используется системный sans-стек Tailwind по умолчанию. Заголовки h1–h4 — `font-weight: 500`, не bold.
- **Компоненты:** полный набор shadcn/ui (button, card, badge, dialog, table, tabs, sidebar, calendar, chart и т.д.) — одинаковый набор файлов во всех 6 проектах, просто используется по-разному.

**Вывод:** ваш вопрос «как свести разные дизайны» на уровне фундамента не стоит — там нечего сводить, это один и тот же дизайн-кит. Работа нужна только на уровне доменных цветов ниже.

## Где реально есть расхождения — доменные цвета (захардкожены в компонентах, не в токенах)

| Экран-источник | Что нашёл | Точные значения |
|---|---|---|
| **Risk Heat Map Radar** — `RiskRadar.tsx` | 5-уровневая шкала серьёзности риска (уже готовая!) | `#22c55e` Low (0–19) → `#eab308` Medium (20–39) → `#f59e0b` High (40–59) → `#ef4444` Critical (60–79) → `#a855f7` Extreme (80–100) |
| **Privacy Risk Register** — `RiskRegister.tsx` | Severity (3 уровня) и Status (3 значения) через Tailwind-классы | Severity: High=`bg-red-100 text-red-800`, Medium=`bg-yellow-100 text-yellow-800`, Low=`bg-green-100 text-green-800`. Status: Open=красный, In Progress=`bg-blue-100 text-blue-800`, Resolved=зелёный |
| **Lessons Learned Table** — `App.tsx` | Impact (High/Medium/Low) теми же 3 цветами, что Severity выше | High=red-100/800, Medium=yellow-100/800, Low=green-100/800 |
| **Knowledge Graph** — `GraphCanvas.tsx` | Узлы графа красятся по типу и по режиму «Color by» | journal-узел=`#8b5cf6` (фиолетовый), funding-узел=`#f59e0b` (оранжевый), publication-узел — из палитры `["#3b82f6","#8b5cf6","#ec4899","#f59e0b","#10b981"]` по хэшу |
| **Agile/Meeting Calendar** (оба) | Типы событий — 3 цвета | Standup/встреча=`bg-blue-500`, Planning=`bg-purple-500`, Retro/Seminar=`bg-green-500` |
| **Privacy Dashboard Sidebar** — `Sidebar.tsx` | Список пунктов навигации + иконки lucide | Dashboard=`Shield`, Calendar=`Calendar`, Risk Register=`AlertTriangle`, Compliance=`CheckCircle`, Reports=`BarChart3`, Settings=`SettingsIcon` |

## Проблема, которую я вижу конкретно для вашего случая

У вас в процессе **своя 4-зонная модель RRA** (Low/Medium/High/Critical, `P×I` с порогами 5/10/16), а в референсе Heat Map Radar — **готовая 5-зонная модель** (добавлена Extreme, пороги по 20 пунктов от 0 до 100). Это разные шкалы, надо явно выбрать одну:

- **Вариант А** — оставить вашу 4-зонную (Low/Medium/High/Critical), просто взять цвета `#22c55e / #eab308 / #f59e0b / #ef4444` из референса (без фиолетового Extreme)
- **Вариант Б** — перейти на 5-зонную как в референсе, добавив Extreme как надмножество Critical (например, RRA=25 при P=I=5 — «Extreme»)

Дальше зависит от вас. Я включил в промт **Вариант А** (без Extreme) как менее ломающий уже согласованную методологию, но это одна строчка поменять, если хотите Extreme.

## Итоговая палитра для RiskLesson (что кладём в промт Claude Code)

```css
--radius: 0.625rem;
--primary: #030213;          /* чёрный, не синий — так во всех референсах */
--border: rgba(0,0,0,.1);
--muted-foreground: #717182;
--destructive: #d4183d;

/* Зоны RRA (P×I), из Risk Heat Map Radar, без Extreme */
--rra-low: #22c55e;
--rra-medium: #eab308;
--rra-high: #f59e0b;
--rra-critical: #ef4444;

/* Статусы риска, из Risk Register */
--status-open: #d4183d;        /* красный — соответствует "Идентификация/Анализ" */
--status-progress: #3b82f6;    /* синий — "Управление/Мониторинг" */
--status-closed: #22c55e;      /* зелёный — "Закрыт" */

/* Календарь — типы событий */
--cal-action: #3b82f6;    /* синий — срок мероприятия */
--cal-review: #a855f7;    /* фиолетовый — пересмотр риска */
--cal-committee: #eab308; /* жёлтый — согласование/комитет */

/* Knowledge Graph — типы узлов */
--node-risk: #3b82f6;
--node-lesson: #8b5cf6;
--node-project: #030213;
```

**Иконки навигации (lucide-react)**, взято из Sidebar.tsx один в один по смыслу:
`Дэшборд → Shield`, `Календарь → Calendar`, `Реестр рисков → AlertTriangle`, `Карта взаимосвязей → GitBranch`, `Матрица рисков → Grid3x3`, `Реестр уроков → BookOpen`, `Privacy Reports & Analytics → BarChart3`

## Что добавить в промт Claude Code

В раздел «Стек» файла `claude_code_prompt.md` смело зафиксируйте (это больше не открытый вопрос):
```
Frontend: React + TypeScript + Vite + Tailwind v4 + shadcn/ui + Radix UI + lucide-react
```
А в конец файла — новый раздел «Дизайн-система» со всем CSS-блоком выше и таблицей доменных цветов. Так Claude Code будет строить компоненты на той же базе, что и референсы, вместо того чтобы придумывать свою.
