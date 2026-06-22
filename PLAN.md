# Lock In — Product Plan

A single-page Vite React app that combines daily todo management, calorie tracking, and focus support into one opinionated personal productivity tool. Built for one person who wants to stop context-switching between three apps.

---

## Goal

Give the user one place to plan the day, track what they eat, and protect deep work — without the friction of separate tools. The app is personal (single-user, localStorage persistence), fast (no backend), and visually aligned to the Claude brand vibe (cream canvas, coral accent, editorial serif display).

---

## Core User Flows

### 1. Morning Setup (5 minutes)
1. Open Lock In.
2. See yesterday's unfinished todos carried forward.
3. Add or remove tasks for today. Each task has a title and optional estimated minutes.
4. See a "total planned time" summary so they don't overcommit.
5. Click **Lock In** to start the day — this activates the focus timer.

### 2. During the Day — Focus Sessions
1. Pick a task from the list, hit **Focus**.
2. A 25-minute countdown starts (Pomodoro-style). During the session, the UI shows only: current task name, timer, a **Give up** button, and a subtle "sessions completed today" counter.
3. When the timer ends: a brief celebration, auto-logged as a completed session, 5-minute break prompt.
4. User can also **Quick Log** a session (manual entry for offline/deep-work that didn't use the timer).

### 3. During the Day — Calorie Logging
1. A dedicated panel (collapsible, not in-your-face) for logging meals.
2. Each entry: description (free text), estimated calories (number), meal type (breakfast/lunch/dinner/snack).
3. Daily calorie target at top, progress bar showing current vs. goal.
4. Quick-add: save common meals as presets for one-tap re-logging.
5. No macro breakdown — keep it simple. Just calories.

### 4. End of Day — Review
1. See: tasks completed / total, total focus sessions, total calories vs. goal.
2. One-click **Reset for tomorrow** clears today's active state, carries unfinished todos forward.

---

## Feature Decisions

| Decision | Rationale |
|---|---|
| **No accounts / no backend** | Personal app. localStorage is fast, zero latency, works offline. No auth burden. |
| **Todos carry forward** | Unfinished tasks auto-appear tomorrow. No "overdue" guilt — just re-plan. |
| **Single Pomodoro length (25 min)** | Reduces decision fatigue. Power users can configure later; v1 ships with one duration. |
| **Calories only, no macros** | Scope discipline. Calorie tracking alone is 80% of the value. Macros invite feature creep. |
| **Presets for common meals** | Reduces logging friction. People eat the same 8-12 things repeatedly. |
| **Focus mode is immersive** | When timer is running, hide todos and calories. One thing at a time. |
| **No notifications / no sound** | The timer is visible on-screen. No dependency on browser notification permissions. |
| **Claude brand vibe** | Cream canvas (#faf9f5), coral primary (#cc785c), serif display (Copernicus), humanist sans body. Light mode only. |
| **Single-page, no router** | Three panels on one page: Tasks | Focus | Calories. Tabs or stacked layout for mobile. |

---

## Data Model (localStorage keys)

```
lockin_tasks        → { id, title, estimatedMinutes, done, createdAt, carriedFrom? }[]
lockin_calories     → { id, description, calories, mealType, loggedAt }[]
lockin_presets      → { id, description, calories, mealType }[]
lockin_sessions     → { id, taskId?, type:'timer'|'manual', durationMinutes, completedAt }[]
lockin_day          → { date: 'YYYY-MM-DD', calorieTarget: number, started: boolean }
```

---

## Layout (Desktop)

```
┌─────────────────────────────────────────────────────┐
│  LOCK IN                           [date] [reset]   │
├──────────────────┬──────────────────┬───────────────┤
│   Tasks          │   Focus          │   Calories    │
│                  │                  │               │
│  [+ add task]    │  [current timer  │  Target: 2200 │
│                  │   or idle state] │  ████░░░ 62%  │
│  ☐ Task 1 (30m) │                  │               │
│  ☑ Task 2 (15m)  │  Sessions: 3     │  [+ log meal] │
│  ☐ Task 3 (45m) │                  │               │
│                  │  [Start Focus]   │  Presets:     │
│  Total: 1h 30m   │                  │  ☕ Oatmeal    │
│                  │                  │  🥗 Salad     │
└──────────────────┴──────────────────┴───────────────┘
```

---

## Implementation Checklist

### Phase 1 — Scaffold & Theme
- [ ] 1. Clean out current App.tsx, App.css (remove Ads Dashboard code). Keep index.css + Tailwind setup.
- [ ] 2. Apply Claude brand vibe to index.css: cream canvas (#faf9f5), coral primary (#cc785c), serif display stack, humanist sans body. Set up CSS variables for colors, radii, typography per the design system.
- [ ] 3. Create minimal App.tsx shell: three-column layout with placeholder panels for Tasks, Focus, Calories.

### Phase 2 — Tasks Panel
- [ ] 4. Implement localStorage read/write helpers (type-safe wrappers with fallback defaults).
- [ ] 5. Tasks panel: render task list, add-task form (title + estimated minutes), checkbox to mark done, display total planned time.
- [ ] 6. Auto-carry unfinished tasks from previous day on app load (check lockin_day.date vs today).
- [ ] 7. Delete task button (with confirmation for tasks that have logged sessions).

### Phase 3 — Focus Panel
- [ ] 8. Focus panel idle state: shows "Start Focus" button, task selector (dropdown of pending tasks), session counter for today.
- [ ] 9. Focus panel active state: 25-minute countdown timer, current task name, "Give up" button (logs partial session), visual progress ring.
- [ ] 10. Timer completion: log session to localStorage, show brief completion state, auto-switch to 5-min break prompt.
- [ ] 11. Manual session logging (Quick Log button): enter minutes, optional task association.

### Phase 4 — Calories Panel
- [ ] 12. Calorie target setting (editable number, stored in lockin_day).
- [ ] 13. Calorie progress bar: total logged today vs. target, with percentage.
- [ ] 14. Log meal form: description, calories, meal type dropdown (breakfast/lunch/dinner/snack).
- [ ] 15. Meal log list for today: show entries, delete button.
- [ ] 16. Presets: save a meal entry as preset, quick-add from preset list, delete preset.

### Phase 5 — Day Lifecycle & Polish
- [ ] 17. "Reset for tomorrow" button: archive today's data (or keep for review), carry unfinished todos forward, clear done flags, set new date.
- [ ] 18. End-of-day summary view (collapsible or shows on reset): tasks done, sessions completed, calories vs. target.
- [ ] 19. Responsive layout: stacked single-column on mobile (<768px) with tab navigation between panels.
- [ ] 20. Final UX writing pass: all button labels, empty states, error messages follow the UX Writing rules from the design system.

### Phase 6 — Verification
- [ ] 21. `npm run build` passes with zero TypeScript errors.
- [ ] 22. `npm run dev` starts, app loads in browser with all three panels visible.
- [ ] 23. Manual smoke test: add task → start focus timer → log calories → verify localStorage keys persist across refresh.
- [ ] 24. Manual smoke test: reset for tomorrow → confirm unfinished tasks carried forward, new date written.

---

## Anti-Patterns to Avoid

- **Dark mode**: Claude vibe is light-only. Do not add a dark mode toggle.
- **Gradients / drop shadows**: Use flat cream surfaces with hairline borders (#e6dfd8). No AI-generic card shadows.
- **Multi-step wizards**: Every action should be one click or one form submit. The app is for speed.
- **"AI" features**: No suggestions, no auto-categorization, no smart anything. The user is in control.
- **Feature creep**: If it's not tasks, calories, or focus, it doesn't belong in v1.