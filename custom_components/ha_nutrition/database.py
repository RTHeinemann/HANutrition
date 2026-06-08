"""SQLite database layer for ha_nutrition."""

import sqlite3
import os
import json
import logging
from datetime import datetime, date
from typing import Optional
from contextlib import contextmanager

_LOGGER = logging.getLogger(__name__)

class NutritionDatabase:
    def __init__(self, db_path: str, db_dir: str):
        self.db_path = db_path
        self.db_dir = db_dir
        self._connection: Optional[sqlite3.Connection] = None
    
    @contextmanager
    def get_connection(self):
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def initialize(self):
        """Create tables and seed data if needed."""
        os.makedirs(self.db_dir, exist_ok=True)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Schema version table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                )
            """)
            
            # Check if already initialized
            cursor.execute("SELECT version FROM schema_migrations LIMIT 1")
            if cursor.fetchone() is not None:
                _LOGGER.info("HANutrition DB already initialized")
                return
            
            # --- Version 1 ---
            # User profiles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Food database
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS food_database (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT,
                    calories_100g REAL,
                    protein_100g REAL,
                    carbs_100g REAL,
                    fat_100g REAL,
                    portation_desc TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Meals
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS meals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    food_name TEXT NOT NULL,
                    calories REAL NOT NULL,
                    protein REAL NOT NULL,
                    carbs REAL NOT NULL,
                    fat REAL NOT NULL,
                    meal_type TEXT NOT NULL,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    food_id TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(food_id) REFERENCES food_database(id)
                )
            """)
            
            # Indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_meals_user_created_at 
                ON meals(user_id, created_at)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_meals_created_at 
                ON meals(created_at)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_meals_food_id 
                ON meals(food_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_food_name 
                ON food_database(name)
            """)
            
            # Seed default user
            cursor.execute("""
                INSERT INTO users (id, display_name, enabled, created_at)
                VALUES (?, ?, ?, ?)
            """, ("default", "Lucas", 1, datetime.now().isoformat()))
            
            # Insert seed foods
            self._seed_foods(conn)
            
            # Mark schema as initialized
            cursor.execute("""
                INSERT INTO schema_migrations (version, applied_at)
                VALUES (1, ?)
            """, (datetime.now().isoformat(),))
            
            _LOGGER.info("HANutrition DB initialized with %d seed foods", len(SEED_FOODS))
    
    def _seed_foods(self, conn: sqlite3.Connection):
        """Insert seed food data."""
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        for food in SEED_FOODS:
            food_id = food["name"].lower().replace(" ", "_").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
            cursor.execute("""
                INSERT OR IGNORE INTO food_database 
                (id, name, category, calories_100g, protein_100g, carbs_100g, fat_100g, portation_desc, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (food_id, food["name"], food["category"], food["calories_100g"], 
                  food["protein_100g"], food["carbs_100g"], food["fat_100g"],
                  food["portation_desc"], now))
    
    # === Meals API ===
    
    def log_meal(self, user_id: str, food_name: str, calories: float, 
                 protein: float, carbs: float, fat: float, meal_type: str, 
                 notes: Optional[str] = None, food_id: Optional[str] = None) -> int:
        """Log a meal entry. Returns meal id."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO meals (user_id, food_name, calories, protein, carbs, fat, meal_type, notes, created_at, food_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, food_name, calories, protein, carbs, fat, meal_type, notes, datetime.now().isoformat(), food_id))
            return cursor.lastrowid
    
    def get_daily_totals(self, user_id: str, target_date: str) -> dict:
        """Get daily nutrition totals. target_date format: YYYY-MM-DD."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(calories), 0) as calories,
                    COALESCE(SUM(protein), 0) as protein,
                    COALESCE(SUM(carbs), 0) as carbs,
                    COALESCE(SUM(fat), 0) as fat,
                    COUNT(*) as meal_count
                FROM meals 
                WHERE user_id = ? 
                AND date(created_at) = ?
            """, (user_id, target_date))
            row = cursor.fetchone()
            return {
                "calories": row["calories"],
                "protein": row["protein"],
                "carbs": row["carbs"],
                "fat": row["fat"],
                "meal_count": row["meal_count"]
            }
    
    def get_daily_meals(self, user_id: str, target_date: str) -> list:
        """Get all meals for a given day."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM meals 
                WHERE user_id = ? 
                AND date(created_at) = ?
                ORDER BY created_at DESC
            """, (user_id, target_date))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_weekly_average(self, user_id: str, days: int = 7) -> dict:
        """Get weekly average macros."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    AVG(daily_calories) as avg_calories,
                    AVG(daily_protein) as avg_protein,
                    AVG(daily_carbs) as avg_carbs,
                    AVG(daily_fat) as avg_fat
                FROM (
                    SELECT 
                        date(created_at) as day,
                        SUM(calories) as daily_calories,
                        SUM(protein) as daily_protein,
                        SUM(carbs) as daily_carbs,
                        SUM(fat) as daily_fat
                    FROM meals 
                    WHERE user_id = ?
                    AND date(created_at) >= date('now', '-' || ? || ' days')
                    GROUP BY date(created_at)
                )
            """, (user_id, days))
            row = cursor.fetchone()
            return {
                "avg_calories": round(row["avg_calories"] or 0, 1),
                "avg_protein": round(row["avg_protein"] or 0, 1),
                "avg_carbs": round(row["avg_carbs"] or 0, 1),
                "avg_fat": round(row["avg_fat"] or 0, 1),
            }
    
    def get_last_meal_time(self, user_id: str) -> Optional[str]:
        """Get the timestamp of the last meal."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT created_at FROM meals 
                WHERE user_id = ? 
                ORDER BY created_at DESC LIMIT 1
            """, (user_id,))
            row = cursor.fetchone()
            return row["created_at"] if row else None
    
    # === Food Database API ===
    
    def add_food(self, name: str, category: str, calories_100g: float, 
                  protein_100g: float, carbs_100g: float, fat_100g: float,
                  portation_desc: str = "100g") -> str:
        """Add food to database. Returns food_id."""
        food_id = name.lower().replace(" ", "_").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO food_database 
                (id, name, category, calories_100g, protein_100g, carbs_100g, fat_100g, portation_desc, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (food_id, name, category, calories_100g, protein_100g, carbs_100g, fat_100g, portation_desc, datetime.now().isoformat()))
            return food_id
    
    def search_food(self, query: str) -> list:
        """Search food database by name."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM food_database 
                WHERE name LIKE ?
                ORDER BY name
                LIMIT 20
            """, (f"%{query}%",))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_food_by_id(self, food_id: str) -> Optional[dict]:
        """Get food by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM food_database WHERE id = ?", (food_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_foods(self) -> list:
        """Get all foods from database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM food_database ORDER BY category, name")
            return [dict(row) for row in cursor.fetchall()]
    
    # === User API ===
    
    def add_user(self, user_id: str, display_name: str) -> bool:
        """Add a new user profile."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO users (id, display_name, enabled, created_at)
                    VALUES (?, ?, 1, ?)
                """, (user_id, display_name, datetime.now().isoformat()))
                return True
            except sqlite3.IntegrityError:
                return False
    
    def set_user_enabled(self, user_id: str, enabled: bool):
        """Enable or disable a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET enabled = ? WHERE id = ?
            """, (1 if enabled else 0, user_id))
    
    def get_all_users(self) -> list:
        """Get all users."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ORDER BY display_name")
            return [dict(row) for row in cursor.fetchall()]


# === Seed Food Data ===
SEED_FOODS = [
    # Gemüse
    {"name": "Brokkoli", "category": "gemüse", "calories_100g": 34, "protein_100g": 2.8, "carbs_100g": 7.0, "fat_100g": 0.4, "portation_desc": "1 Bund = 300g"},
    {"name": "Karotte", "category": "gemüse", "calories_100g": 41, "protein_100g": 0.9, "carbs_100g": 10.0, "fat_100g": 0.2, "portation_desc": "1 Stück = 70g"},
    {"name": "Zucchini", "category": "gemüse", "calories_100g": 17, "protein_100g": 1.2, "carbs_100g": 3.1, "fat_100g": 0.3, "portation_desc": "1 Stück = 200g"},
    {"name": "Paprika", "category": "gemüse", "calories_100g": 27, "protein_100g": 1.0, "carbs_100g": 5.3, "fat_100g": 0.3, "portation_desc": "1 Stück = 150g"},
    {"name": "Tomate", "category": "gemüse", "calories_100g": 18, "protein_100g": 0.9, "carbs_100g": 3.9, "fat_100g": 0.2, "portation_desc": "1 Stück = 120g"},
    {"name": "Gurke", "category": "gemüse", "calories_100g": 16, "protein_100g": 0.7, "carbs_100g": 3.6, "fat_100g": 0.1, "portation_desc": "1 Stück = 300g"},
    {"name": "Spinat", "category": "gemüse", "calories_100g": 23, "protein_100g": 2.9, "carbs_100g": 3.6, "fat_100g": 0.3, "portation_desc": "1 Packung TK = 250g"},
    {"name": "Kartoffel", "category": "gemüse", "calories_100g": 77, "protein_100g": 2.0, "carbs_100g": 17.0, "fat_100g": 0.1, "portation_desc": "1 Stück = 150g"},
    {"name": "Süßkartoffel", "category": "gemüse", "calories_100g": 86, "protein_100g": 1.6, "carbs_100g": 20.0, "fat_100g": 0.1, "portation_desc": "1 Stück = 130g"},
    {"name": "Zwiebel", "category": "gemüse", "calories_100g": 40, "protein_100g": 1.1, "carbs_100g": 9.3, "fat_100g": 0.1, "portation_desc": "1 Stück = 150g"},
    {"name": "Kürbis (Kabeljau)", "category": "gemüse", "calories_100g": 26, "protein_100g": 1.2, "carbs_100g": 4.7, "fat_100g": 0.2, "portation_desc": "1 Packung = 500g"},
    
    # Obst
    {"name": "Banane", "category": "obst", "calories_100g": 89, "protein_100g": 1.1, "carbs_100g": 23.0, "fat_100g": 0.3, "portation_desc": "1 Stück = 120g"},
    {"name": "Apfel", "category": "obst", "calories_100g": 52, "protein_100g": 0.3, "carbs_100g": 14.0, "fat_100g": 0.2, "portation_desc": "1 Stück = 180g"},
    {"name": "Orange", "category": "obst", "calories_100g": 47, "protein_100g": 0.9, "carbs_100g": 12.0, "fat_100g": 0.1, "portation_desc": "1 Stück = 180g"},
    {"name": "Erdbeere", "category": "obst", "calories_100g": 33, "protein_100g": 0.7, "carbs_100g": 7.7, "fat_100g": 0.3, "portation_desc": "100g = ca. 6-8 Stück"},
    {"name": "Himbeere", "category": "obst", "calories_100g": 52, "protein_100g": 1.2, "carbs_100g": 12.0, "fat_100g": 0.7, "portation_desc": "100g = ca. 80 Stück"},
    {"name": "Blaubeere", "category": "obst", "calories_100g": 57, "protein_100g": 0.7, "carbs_100g": 14.0, "fat_100g": 0.3, "portation_desc": "100g = ca. 100 Stück"},
    {"name": "Kiwi", "category": "obst", "calories_100g": 61, "protein_100g": 1.1, "carbs_100g": 15.0, "fat_100g": 0.5, "portation_desc": "1 Stück = 75g"},
    {"name": "Pfirsich", "category": "obst", "calories_100g": 39, "protein_100g": 1.0, "carbs_100g": 10.0, "fat_100g": 0.3, "portation_desc": "1 Stück = 150g"},
    
    # Fleisch & Fisch
    {"name": "Hähnchenbrust", "category": "fleisch", "calories_100g": 165, "protein_100g": 31.0, "carbs_100g": 0.0, "fat_100g": 3.6, "portation_desc": "1 Portion = 200g"},
    {"name": "Putenbrust", "category": "fleisch", "calories_100g": 104, "protein_100g": 23.0, "carbs_100g": 0.0, "fat_100g": 1.0, "portation_desc": "1 Portion = 200g"},
    {"name": "Rinderhack (5% Fett)", "category": "fleisch", "calories_100g": 188, "protein_100g": 18.0, "carbs_100g": 0.0, "fat_100g": 12.0, "portation_desc": "1 Portion = 200g"},
    {"name": "Rinderfilet", "category": "fleisch", "calories_100g": 180, "protein_100g": 26.0, "carbs_100g": 0.0, "fat_100g": 8.0, "portation_desc": "1 Portion = 200g"},
    {"name": "Lachs", "category": "fisch", "calories_100g": 208, "protein_100g": 20.0, "carbs_100g": 0.0, "fat_100g": 13.0, "portation_desc": "1 Portion = 150g"},
    {"name": "Thunfisch (im eigenen Saft)", "category": "fisch", "calories_100g": 116, "protein_100g": 26.0, "carbs_100g": 0.0, "fat_100g": 1.0, "portation_desc": "1 Dose = 160g abgetropft"},
    {"name": "Forelle", "category": "fisch", "calories_100g": 119, "protein_100g": 21.0, "carbs_100g": 0.0, "fat_100g": 3.5, "portation_desc": "1 Stück = 200g"},
    {"name": "Kabeljau", "category": "fisch", "calories_100g": 82, "protein_100g": 18.0, "carbs_100g": 0.0, "fat_100g": 0.7, "portation_desc": "1 Portion = 200g"},
    
    # Milchprodukte
    {"name": "Vollmilch (3.5% Fett)", "category": "milchprodukte", "calories_100g": 61, "protein_100g": 3.3, "carbs_100g": 4.7, "fat_100g": 3.5, "portation_desc": "1 Glas = 200ml"},
    {"name": "Magerquark", "category": "milchprodukte", "calories_100g": 72, "protein_100g": 12.0, "carbs_100g": 4.0, "fat_100g": 0.3, "portation_desc": "1 Becher = 250g"},
    {"name": "Griechischer Joghurt (2% Fett)", "category": "milchprodukte", "calories_100g": 59, "protein_100g": 9.0, "carbs_100g": 3.6, "fat_100g": 2.0, "portation_desc": "1 Becher = 150g"},
    {"name": "Hüttenkäse (5% Fett)", "category": "milchprodukte", "calories_100g": 98, "protein_100g": 12.0, "carbs_100g": 3.4, "fat_100g": 5.0, "portation_desc": "1 Packung = 250g"},
    {"name": "Mozzarella", "category": "milchprodukte", "calories_100g": 280, "protein_100g": 28.0, "carbs_100g": 3.1, "fat_100g": 17.0, "portation_desc": "1 Kugel = 125g"},
    {"name": "Cheddar", "category": "milchprodukte", "calories_100g": 403, "protein_100g": 25.0, "carbs_100g": 1.3, "fat_100g": 33.0, "portation_desc": "1 Scheibe = 20g"},
    {"name": "Parmesan", "category": "milchprodukte", "calories_100g": 431, "protein_100g": 38.0, "carbs_100g": 3.2, "fat_100g": 29.0, "portation_desc": "1 Portion = 20g"},
    {"name": "Sahne (15% Fett)", "category": "milchprodukte", "calories_100g": 156, "protein_100g": 2.0, "carbs_100g": 3.2, "fat_100g": 15.0, "portation_desc": "1 EL = 15ml"},
    {"name": "Butter", "category": "milchprodukte", "calories_100g": 717, "protein_100g": 0.9, "carbs_100g": 0.1, "fat_100g": 81.0, "portation_desc": "1 Scheibe = 8g"},
    {"name": "Ei (Größe M)", "category": "milchprodukte", "calories_100g": 155, "protein_100g": 13.0, "carbs_100g": 1.1, "fat_100g": 11.0, "portation_desc": "1 Stück = 55g"},
    {"name": "Eiweiß", "category": "milchprodukte", "calories_100g": 52, "protein_100g": 11.0, "carbs_100g": 0.7, "fat_100g": 0.0, "portation_desc": "1 Eiweiß = 33g"},
    
    # Getreide & Kohlenhydrate
    {"name": "Reis (Basmati, roh)", "category": "getreide", "calories_100g": 344, "protein_100g": 7.1, "carbs_100g": 77.0, "fat_100g": 0.7, "portation_desc": "1 Portion = 80g"},
    {"name": "Reis (gekocht)", "category": "getreide", "calories_100g": 130, "protein_100g": 2.7, "carbs_100g": 28.0, "fat_100g": 0.3, "portation_desc": "1 Portion = 200g"},
    {"name": "Nudeln (Vollkorn, roh)", "category": "getreide", "calories_100g": 336, "protein_100g": 13.0, "carbs_100g": 69.0, "fat_100g": 2.5, "portation_desc": "1 Portion = 80g"},
    {"name": "Vollkornbrot", "category": "getreide", "calories_100g": 246, "protein_100g": 11.0, "carbs_100g": 41.0, "fat_100g": 3.4, "portation_desc": "1 Scheibe = 40g"},
    {"name": "Weizenbrot (hell)", "category": "getreide", "calories_100g": 265, "protein_100g": 9.0, "carbs_100g": 50.0, "fat_100g": 3.5, "portation_desc": "1 Scheibe = 35g"},
    {"name": "Haferflocken", "category": "getreide", "calories_100g": 389, "protein_100g": 16.0, "carbs_100g": 66.0, "fat_100g": 6.9, "portation_desc": "1 Portion = 50g"},
    {"name": "Reiswaffel", "category": "getreide", "calories_100g": 380, "protein_100g": 6.4, "carbs_100g": 81.0, "fat_100g": 2.7, "portation_desc": "1 Stück = 9g"},
    
    # Hülsenfrüchte & Nüsse
    {"name": "Kichererbsen (gekocht)", "category": "hülsenfrüchte", "calories_100g": 164, "protein_100g": 8.9, "carbs_100g": 27.0, "fat_100g": 2.6, "portation_desc": "1 Dose = 400g abgetropft"},
    {"name": "Linsen (gekocht)", "category": "hülsenfrüchte", "calories_100g": 116, "protein_100g": 9.0, "carbs_100g": 20.0, "fat_100g": 0.4, "portation_desc": "1 Portion = 200g"},
    {"name": "Weiße Bohnen (gekocht)", "category": "hülsenfrüchte", "calories_100g": 139, "protein_100g": 8.7, "carbs_100g": 25.0, "fat_100g": 0.5, "portation_desc": "1 Dose = 400g abgetropft"},
    {"name": "Mandeln", "category": "nüsse", "calories_100g": 579, "protein_100g": 21.0, "carbs_100g": 22.0, "fat_100g": 49.0, "portation_desc": "1 Portion = 30g (ca. 20 Stück)"},
    {"name": "Walnüsse", "category": "nüsse", "calories_100g": 654, "protein_100g": 15.0, "carbs_100g": 14.0, "fat_100g": 65.0, "portation_desc": "1 Portion = 30g"},
    {"name": "Erdnüsse", "category": "nüsse", "calories_100g": 567, "protein_100g": 26.0, "carbs_100g": 16.0, "fat_100g": 49.0, "portation_desc": "1 Portion = 30g"},
    {"name": "Chiasamen", "category": "nüsse", "calories_100g": 486, "protein_100g": 17.0, "carbs_100g": 42.0, "fat_100g": 31.0, "portation_desc": "1 Portion = 30g"},
    {"name": "Leinsamen", "category": "nüsse", "calories_100g": 534, "protein_100g": 18.0, "carbs_100g": 29.0, "fat_100g": 42.0, "portation_desc": "1 Portion = 20g"},
    
    # Sonstiges
    {"name": "Olivenöl", "category": "sonstige", "calories_100g": 884, "protein_100g": 0.0, "carbs_100g": 0.0, "fat_100g": 100.0, "portation_desc": "1 EL = 15ml"},
    {"name": "Honig", "category": "sonstige", "calories_100g": 304, "protein_100g": 0.3, "carbs_100g": 82.0, "fat_100g": 0.0, "portation_desc": "1 TL = 7g"},
    {"name": "Proteinpulver (Whey, Vanille)", "category": "sonstige", "calories_100g": 370, "protein_100g": 80.0, "carbs_100g": 4.0, "fat_100g": 5.0, "portation_desc": "1 Scoop = 30g"},
]
