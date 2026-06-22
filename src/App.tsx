import { type ReactNode, useEffect, useMemo, useState } from "react";
import {
  Flame,
  Focus,
  ListTodo,
  Plus,
  Salad,
  TimerReset,
  CheckCircle2,
  Circle,
  Trash2,
  Clock3,
  Brain,
  Zap,
  Target,
  Coffee,
  MoonStar,
  SunMedium,
} from "lucide-react";
import "./App.css";

type Energy = "low" | "medium" | "high";
type MealType = "breakfast" | "lunch" | "dinner" | "snack";

type Task = {
  id: string;
  title: string;
  energy: Energy;
  minutes: number;
  done: boolean;
};

type Meal = {
  id: string;
  title: string;
  calories: number;
  type: MealType;
};

type FocusPreset = {
  label: string;
  minutes: number;
};

type Blocker = {
  id: string;
  label: string;
  done: boolean;
};

const TASKS_SEED: Task[] = [
  { id: "task-1", title: "Ship homepage revision", energy: "high", minutes: 90, done: false },
  { id: "task-2", title: "Review growth dashboard", energy: "medium", minutes: 35, done: false },
  { id: "task-3", title: "Clear founder inbox", energy: "low", minutes: 20, done: true },
  { id: "task-4", title: "Draft LinkedIn post", energy: "medium", minutes: 25, done: false },
];

const MEALS_SEED: Meal[] = [
  { id: "meal-1", title: "Eggs and toast", calories: 430, type: "breakfast" },
  { id: "meal-2", title: "Chicken rice bowl", calories: 610, type: "lunch" },
  { id: "meal-3", title: "Protein yogurt", calories: 220, type: "snack" },
];

const PRESETS: FocusPreset[] = [
  { label: "Sprint", minutes: 25 },
  { label: "Deep block", minutes: 50 },
  { label: "Long push", minutes: 75 },
  { label: "Recovery", minutes: 15 },
];

const BLOCKERS_SEED: Blocker[] = [
  { id: "b1", label: "Phone face down", done: true },
  { id: "b2", label: "Inbox closed", done: false },
  { id: "b3", label: "Slack muted", done: false },
  { id: "b4", label: "Water on desk", done: true },
];

const CUES = [
  "Do the next hard thing.",
  "Protect the block. Ignore the noise.",
  "Small reps compound.",
  "Finish before you switch.",
  "The timer is your contract.",
];

const ENERGY_LABELS: Record<Energy, string> = {
  low: "Low drag",
  medium: "Steady",
  high: "Heavy lift",
};

const MEAL_LABELS: Record<MealType, string> = {
  breakfast: "Breakfast",
  lunch: "Lunch",
  dinner: "Dinner",
  snack: "Snack",
};

function formatMinutes(total: number) {
  if (total < 60) return `${total}m`;
  const hours = Math.floor(total / 60);
  const mins = total % 60;
  return mins ? `${hours}h ${mins}m` : `${hours}h`;
}

function formatClock(seconds: number) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}

function sectionTitle(icon: React.ReactNode, title: string, meta?: string) {
  return (
    <div className="section-title">
      <div className="section-title__left">
        <span className="section-title__icon">{icon}</span>
        <div>
          <h2>{title}</h2>
          {meta ? <p>{meta}</p> : null}
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [tasks, setTasks] = useState<Task[]>(TASKS_SEED);
  const [meals, setMeals] = useState<Meal[]>(MEALS_SEED);
  const [blockers, setBlockers] = useState<Blocker[]>(BLOCKERS_SEED);
  const [taskTitle, setTaskTitle] = useState("");
  const [taskMinutes, setTaskMinutes] = useState(30);
  const [taskEnergy, setTaskEnergy] = useState<Energy>("medium");
  const [mealTitle, setMealTitle] = useState("");
  const [mealCalories, setMealCalories] = useState(450);
  const [mealType, setMealType] = useState<MealType>("dinner");
  const [targetCalories, setTargetCalories] = useState(2200);
  const [selectedPreset, setSelectedPreset] = useState<FocusPreset>(PRESETS[0]);
  const [secondsLeft, setSecondsLeft] = useState(PRESETS[0].minutes * 60);
  const [isRunning, setIsRunning] = useState(false);
  const [focusMinutes, setFocusMinutes] = useState(95);
  const [cueIndex, setCueIndex] = useState(0);

  useEffect(() => {
    if (!isRunning) return;
    const timer = window.setInterval(() => {
      setSecondsLeft((current) => {
        if (current <= 1) {
          window.clearInterval(timer);
          setIsRunning(false);
          setFocusMinutes((value) => value + selectedPreset.minutes);
          setCueIndex((value) => (value + 1) % CUES.length);
          return selectedPreset.minutes * 60;
        }
        return current - 1;
      });
    }, 1000);

    return () => window.clearInterval(timer);
  }, [isRunning, selectedPreset]);

  useEffect(() => {
    if (!isRunning) {
      setSecondsLeft(selectedPreset.minutes * 60);
    }
  }, [selectedPreset, isRunning]);

  const doneTasks = tasks.filter((task) => task.done).length;
  const totalTaskMinutes = tasks.filter((task) => !task.done).reduce((sum, task) => sum + task.minutes, 0);
  const totalCalories = meals.reduce((sum, meal) => sum + meal.calories, 0);
  const remainingCalories = targetCalories - totalCalories;
  const blockerScore = blockers.filter((item) => item.done).length;
  const currentCue = CUES[cueIndex];

  const nextTask = useMemo(() => tasks.find((task) => !task.done) ?? null, [tasks]);

  function addTask() {
    const title = taskTitle.trim();
    if (!title) return;

    setTasks((current) => [
      {
        id: crypto.randomUUID(),
        title,
        minutes: taskMinutes,
        energy: taskEnergy,
        done: false,
      },
      ...current,
    ]);
    setTaskTitle("");
    setTaskMinutes(30);
    setTaskEnergy("medium");
  }

  function addMeal() {
    const title = mealTitle.trim();
    if (!title || mealCalories <= 0) return;

    setMeals((current) => [
      {
        id: crypto.randomUUID(),
        title,
        calories: mealCalories,
        type: mealType,
      },
      ...current,
    ]);
    setMealTitle("");
    setMealCalories(450);
    setMealType("dinner");
  }

  function toggleTask(id: string) {
    setTasks((current) => current.map((task) => (task.id === id ? { ...task, done: !task.done } : task)));
  }

  function removeTask(id: string) {
    setTasks((current) => current.filter((task) => task.id !== id));
  }

  function removeMeal(id: string) {
    setMeals((current) => current.filter((meal) => meal.id !== id));
  }

  function toggleBlocker(id: string) {
    setBlockers((current: any) => current.map((item: Blocker) => (item.id === id ? { ...item, done: !item.done } : item)));
  }

  function startFocus(minutes: number) {
    const preset = PRESETS.find((item) => item.minutes === minutes) ?? PRESETS[0];
    setSelectedPreset(preset);
    setSecondsLeft(preset.minutes * 60);
    setIsRunning(true);
  }

  function resetFocus() {
    setIsRunning(false);
    setSecondsLeft(selectedPreset.minutes * 60);
  }

  const calorieProgress = Math.min((totalCalories / targetCalories) * 100, 100);

  return (
    <div className="app-shell">
      <div className="hero-panel">
        <div>
          <div className="eyebrow">Operator mode</div>
          <h1>Lock In</h1>
          <p className="hero-copy">
            One board for tasks, calories, and focus. Keep the day tight. Reduce drift.
          </p>
        </div>
        <div className="hero-stats">
          <div className="hero-stat">
            <span>Tasks done</span>
            <strong>{doneTasks}/{tasks.length}</strong>
          </div>
          <div className="hero-stat">
            <span>Calories left</span>
            <strong>{remainingCalories >= 0 ? remainingCalories : 0}</strong>
          </div>
          <div className="hero-stat">
            <span>Focus bank</span>
            <strong>{formatMinutes(focusMinutes)}</strong>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        <section className="panel panel--tasks">
          {sectionTitle(<ListTodo size={18} />, "Task stack", `${tasks.length} active items`)}
          <div className="composer">
            <input value={taskTitle} onChange={(e) => setTaskTitle(e.target.value)} placeholder="Add a task" />
            <div className="composer__row">
              <select value={taskEnergy} onChange={(e) => setTaskEnergy(e.target.value as Energy)}>
                {Object.entries(ENERGY_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
              <input type="number" min={5} step={5} value={taskMinutes} onChange={(e) => setTaskMinutes(Number(e.target.value))} />
              <button onClick={addTask}><Plus size={16} /> Add</button>
            </div>
          </div>

          <div className="task-summary">
            <div>
              <span>Next up</span>
              <strong>{nextTask ? nextTask.title : "Everything cleared"}</strong>
            </div>
            <div>
              <span>Remaining load</span>
              <strong>{formatMinutes(totalTaskMinutes)}</strong>
            </div>
          </div>

          <div className="task-list">
            {tasks.map((task) => (
              <div key={task.id} className={`task-row ${task.done ? "task-row--done" : ""}`}>
                <button className="icon-button" onClick={() => toggleTask(task.id)}>
                  {task.done ? <CheckCircle2 size={18} /> : <Circle size={18} />}
                </button>
                <div className="task-row__body">
                  <strong>{task.title}</strong>
                  <div className="task-row__meta">
                    <span className={`pill pill--${task.energy}`}>{ENERGY_LABELS[task.energy]}</span>
                    <span><Clock3 size={14} /> {task.minutes} min</span>
                  </div>
                </div>
                <button className="icon-button icon-button--danger" onClick={() => removeTask(task.id)}>
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        </section>

        <section className="panel panel--focus">
          {sectionTitle(<Focus size={18} />, "Focus mode", isRunning ? "Session live" : "Ready to start")}
          <div className="timer-card">
            <div className="timer-card__ring">
              <span>{formatClock(secondsLeft)}</span>
              <small>{selectedPreset.label}</small>
            </div>
            <div className="timer-card__side">
              <p className="cue">{currentCue}</p>
              <div className="preset-list">
                {PRESETS.map((preset) => (
                  <button
                    key={preset.label}
                    className={preset.minutes === selectedPreset.minutes ? "is-active" : ""}
                    onClick={() => startFocus(preset.minutes)}
                  >
                    <TimerReset size={15} /> {preset.label} · {preset.minutes}m
                  </button>
                ))}
              </div>
              <div className="focus-actions">
                <button className="button button--primary" onClick={() => setIsRunning((value) => !value)}>
                  {isRunning ? <MoonStar size={16} /> : <Zap size={16} />}
                  {isRunning ? "Pause session" : "Start now"}
                </button>
                <button className="button button--ghost" onClick={resetFocus}>
                  <SunMedium size={16} /> Reset
                </button>
              </div>
            </div>
          </div>

          <div className="focus-checklist">
            <div className="focus-checklist__header">
              <strong>Lock-in checklist</strong>
              <span>{blockerScore}/{blockers.length} done</span>
            </div>
            {blockers.map((item) => (
              <button key={item.id} className={`check-row ${item.done ? "check-row--done" : ""}`} onClick={() => toggleBlocker(item.id)}>
                {item.done ? <CheckCircle2 size={16} /> : <Circle size={16} />}
                <span>{item.label}</span>
              </button>
            ))}
          </div>
        </section>

        <section className="panel panel--calories">
          {sectionTitle(<Flame size={18} />, "Calories", `${totalCalories}/${targetCalories}`)}
          <div className="macro-card">
            <div className="macro-card__top">
              <div>
                <span>Daily target</span>
                <strong>{targetCalories} kcal</strong>
              </div>
              <input type="number" min={1200} step={50} value={targetCalories} onChange={(e) => setTargetCalories(Number(e.target.value))} />
            </div>
            <div className="progress-track">
              <div className="progress-bar" style={{ width: `${calorieProgress}%` }} />
            </div>
            <div className="macro-card__bottom">
              <span>{remainingCalories > 0 ? `${remainingCalories} kcal left` : "Target hit"}</span>
              <strong>{Math.round(calorieProgress)}%</strong>
            </div>
          </div>

          <div className="composer">
            <input value={mealTitle} onChange={(e) => setMealTitle(e.target.value)} placeholder="Log a meal" />
            <div className="composer__row">
              <select value={mealType} onChange={(e) => setMealType(e.target.value as MealType)}>
                {Object.entries(MEAL_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
              <input type="number" min={0} step={10} value={mealCalories} onChange={(e) => setMealCalories(Number(e.target.value))} />
              <button onClick={addMeal}><Salad size={16} /> Save</button>
            </div>
          </div>

          <div className="meal-list">
            {meals.map((meal) => (
              <div key={meal.id} className="meal-row">
                <div>
                  <strong>{meal.title}</strong>
                  <span>{MEAL_LABELS[meal.type]}</span>
                </div>
                <div className="meal-row__right">
                  <strong>{meal.calories}</strong>
                  <button className="icon-button icon-button--danger" onClick={() => removeMeal(meal.id)}>
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>

      <div className="bottom-strip">
        <div className="mini-panel">
          <Brain size={18} />
          <div>
            <span>Focus cue</span>
            <strong>{currentCue}</strong>
          </div>
        </div>
        <div className="mini-panel">
          <Target size={18} />
          <div>
            <span>Best next move</span>
            <strong>{nextTask ? nextTask.title : "Shut down clean"}</strong>
          </div>
        </div>
        <div className="mini-panel">
          <Coffee size={18} />
          <div>
            <span>Fuel status</span>
            <strong>{remainingCalories > 400 ? "Plenty left" : "Plan dinner now"}</strong>
          </div>
        </div>
      </div>
    </div>
  );
}
