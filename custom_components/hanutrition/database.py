"""HANutrition nutrition database with SQLite."""

import sqlite3
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any
import json
import logging

_LOGGER = logging.getLogger(__name__)

# Food database with realistic nutritional info
FOOD_DATABASE: Dict[str, Dict[str, Any]] = {
    # Basic foods
    "apfel": {"name": "Apfel", "calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2, "serving_g": 182},
    "banane": {"name": "Banane", "calories": 89, "protein": 1.1, "carbs": 23, "fat": 0.3, "serving_g": 118},
    "reis": {"name": "Reis", "calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3, "serving_g": 100},
    "nudeln": {"name": "Nudeln", "calories": 131, "protein": 5.0, "carbs": 25, "fat": 1.1, "serving_g": 100},
    "kartoffel": {"name": "Kartoffel", "calories": 77, "protein": 2.0, "carbs": 17, "fat": 0.1, "serving_g": 170},
    "huhn": {"name": "Hähnchenbrust", "calories": 165, "protein": 31, "carbs": 0, "fat": 3.6, "serving_g": 100},
    "lachs": {"name": "Lachs", "calories": 208, "protein": 20, "carbs": 0, "fat": 13, "serving_g": 100},
    "ei": {"name": "Ei", "calories": 155, "protein": 13, "carbs": 1.1, "fat": 11, "serving_g": 50},
    "milch": {"name": "Milch", "calories": 42, "protein": 3.4, "carbs": 5, "fat": 1, "serving_g": 100},
    "joghurt": {"name": "Joghurt", "calories": 59, "protein": 11, "carbs": 3.6, "fat": 1, "serving_g": 100},
    "kase": {"name": "Käse", "calories": 350, "protein": 25, "carbs": 1.3, "fat": 27, "serving_g": 100},
    "brot": {"name": "Brot", "calories": 265, "protein": 9, "carbs": 49, "fat": 3.2, "serving_g": 100},
    "haferflocken": {"name": "Haferflocken", "calories": 389, "protein": 17, "carbs": 66, "fat": 7, "serving_g": 100},
    "magerquark": {"name": "Magerquark", "calories": 72, "protein": 12, "carbs": 4, "fat": 1, "serving_g": 100},
    "brokkoli": {"name": "Brokkoli", "calories": 34, "protein": 2.8, "carbs": 7, "fat": 0.4, "serving_g": 91},
    "salat": {"name": "Salat", "calories": 15, "protein": 1.4, "carbs": 3, "fat": 0.2, "serving_g": 85},
    "tomate": {"name": "Tomate", "calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2, "serving_g": 123},
    "gurke": {"name": "Gurke", "calories": 15, "protein": 0.7, "carbs": 3.6, "fat": 0.1, "serving_g": 301},
    "pizza": {"name": "Pizza", "calories": 266, "protein": 11, "carbs": 33, "fat": 10, "serving_g": 100},
    "schnitzel": {"name": "Schnitzel", "calories": 240, "protein": 28, "carbs": 8, "fat": 12, "serving_g": 150},
    "suppe": {"name": "Suppe", "calories": 45, "protein": 3, "carbs": 5, "fat": 1.5, "serving_g": 250},
    "kaffee": {"name": "Kaffee", "calories": 2, "protein": 0.1, "carbs": 0, "fat": 0, "serving_g": 200},
    "tee": {"name": "Tee", "calories": 1, "protein": 0, "carbs": 0, "fat": 0, "serving_g": 250},
    "bier": {"name": "Bier", "calories": 43, "protein": 0.5, "carbs": 3.6, "fat": 0, "serving_g": 330},
    "wein": {"name": "Wein", "calories": 82, "protein": 0.1, "carbs": 2.6, "fat": 0, "serving_g": 100},
    "shakes": {"name": "Proteinshake", "calories": 120, "protein": 24, "carbs": 3, "fat": 1, "serving_g": 300},
    "nuess": {"name": "Nüsse", "calories": 600, "protein": 20, "carbs": 20, "fat": 50, "serving_g": 100},
    "schokolade": {"name": "Schokolade", "calories": 546, "protein": 5, "carbs": 59, "fat": 31, "serving_g": 100},
    "toast": {"name": "Toast", "calories": 266, "protein": 9, "carbs": 49, "fat": 3.2, "serving_g": 33},
    "bratwurst": {"name": "Bratwurst", "calories": 290, "protein": 20, "carbs": 1, "fat": 23, "serving_g": 60},
    "currywurst": {"name": "Currywurst", "calories": 340, "protein": 22, "carbs": 15, "fat": 22, "serving_g": 200},
    "döner": {"name": "Döner", "calories": 400, "protein": 20, "carbs": 30, "fat": 22, "serving_g": 300},
    "spaghetti": {"name": "Spaghetti Bolognese", "calories": 180, "protein": 8, "carbs": 30, "fat": 4, "serving_g": 250},
    "pudding": {"name": "Pudding", "calories": 90, "protein": 3, "carbs": 15, "fat": 2.5, "serving_g": 125},
    "reiswaffel": {"name": "Reiswaffel", "calories": 380, "protein": 6, "carbs": 81, "fat": 3, "serving_g": 9},
    "musli": {"name": "Musli", "calories": 400, "protein": 9, "carbs": 52, "fat": 18, "serving_g": 100},
    "bohnens": {"name": "Bohnen", "calories": 127, "protein": 8.7, "carbs": 22, "fat": 0.5, "serving_g": 100},
    "linsen": {"name": "Linsen", "calories": 116, "protein": 9, "carbs": 20, "fat": 0.4, "serving_g": 100},
    "kichererbse": {"name": "Kichererbse", "calories": 164, "protein": 8.9, "carbs": 27, "fat": 2.6, "serving_g": 100},
    "avocado": {"name": "Avocado", "calories": 160, "protein": 2, "carbs": 9, "fat": 15, "serving_g": 150},
    "lachs_rauch": {"name": "Räucherlachs", "calories": 117, "protein": 18, "carbs": 0, "fat": 4.3, "serving_g": 100},
    "thunfisch": {"name": "Thunfisch (Dose)", "calories": 116, "protein": 26, "carbs": 0, "fat": 1, "serving_g": 100},
    "creme_fraiche": {"name": "Crème fraîche", "calories": 310, "protein": 3, "carbs": 3, "fat": 31, "serving_g": 30},
    "sojasauce": {"name": "Sojasauce", "calories": 53, "protein": 8, "carbs": 5, "fat": 0, "serving_g": 15},
    "honig": {"name": "Honig", "calories": 304, "protein": 0.3, "carbs": 82, "fat": 0, "serving_g": 30},
    "olivenol": {"name": "Olivenöl", "calories": 884, "protein": 0, "carbs": 0, "fat": 100, "serving_g": 15},
    "butter": {"name": "Butter", "calories": 717, "protein": 0.9, "carbs": 0.1, "fat": 81, "serving_g": 10},
    "zwiebel": {"name": "Zwiebel", "calories": 40, "protein": 1.1, "carbs": 9, "fat": 0.1, "serving_g": 110},
    "karotte": {"name": "Karotte", "calories": 41, "protein": 0.9, "carbs": 10, "fat": 0.2, "serving_g": 61},
    "paprika": {"name": "Paprika", "calories": 31, "protein": 1, "carbs": 6, "fat": 0.3, "serving_g": 119},
    "champignon": {"name": "Champignon", "calories": 22, "protein": 3.1, "carbs": 3.3, "fat": 0.3, "serving_g": 70},
    "spinat": {"name": "Spinat", "calories": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4, "serving_g": 30},
}


class NutritionDatabase:
    """SQLite database for nutrition tracking."""
    
    def __init__(self, db_path: str, db_dir: str):
        """Initialize the database."""
        self.db_path = db_path
        self.db_dir = db_dir
        self._conn: Optional[sqlite3.Connection] = None
    
    def initialize(self) -> None:
        """Create database and tables if they don't exist."""
        os.makedirs(self.db_dir, exist_ok=True)
        
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        
        cursor = self._conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                goal_calories REAL DEFAULT 2500,
                goal_protein REAL DEFAULT 200,
                goal_carbs REAL DEFAULT 300,
                goal_fat REAL DEFAULT 70,
                active INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Meals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                meal_type TEXT NOT NULL,
                meal_date TEXT NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Food entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS food_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meal_id INTEGER NOT NULL,
                food_name TEXT NOT NULL,
                calories REAL NOT NULL,
                protein REAL NOT NULL,
                carbs REAL NOT NULL,
                fat REAL NOT NULL,
                serving_g REAL,
                serving_unit TEXT DEFAULT 'g',
                quantity REAL DEFAULT 1,
                FOREIGN KEY (meal_id) REFERENCES meals(id)
            )
        """)
        
        # Food database table (for lookups)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS food_db (
                name TEXT PRIMARY KEY,
                calories REAL NOT NULL,
                protein REAL NOT NULL,
                carbs REAL NOT NULL,
                fat REAL NOT NULL,
                serving_g REAL,
                serving_unit TEXT DEFAULT 'g'
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_meals_user_date 
            ON meals(user_id, meal_date)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_food_entries_meal 
            ON food_entries(meal_id)
        """)
        
        self._conn.commit()
        
        # Seed with food database
        self._seed_food_database()
        
        # Create default user if none exists
        self._ensure_default_user()
        
        _LOGGER.info("HANutrition database initialized at %s", self.db_path)
    
    def _seed_food_database(self) -> None:
        """Populate food database table with common foods."""
        cursor = self._conn.cursor()
        
        for name, info in FOOD_DATABASE.items():
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO food_db (name, calories, protein, carbs, fat, serving_g, serving_unit)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    name,
                    info["calories"],
                    info["protein"],
                    info["carbs"],
                    info["fat"],
                    info["serving_g"],
                    info.get("serving_g", "g"),
                ))
            except Exception as e:
                _LOGGER.error("Error seeding food '%s': %s", name, e)
        
        self._conn.commit()
    
    def _ensure_default_user(self) -> None:
        """Create default user if no users exist."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        
        if count == 0:
            cursor.execute("""
                INSERT INTO users (name, email, goal_calories, goal_protein, goal_carbs, goal_fat)
                VALUES ('User', 'user@home.local', 2500, 200, 300, 70)
            """)
            self._conn.commit()
            _LOGGER.info("Default user created")
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        if not self._conn:
            self.initialize()
        return self._conn
    
    def log_meal(self, user_id: int, meal_type: str, food_name: str, 
                 calories: float, protein: float, carbs: float, fat: float,
                 serving_g: float = 100, quantity: float = 1) -> int:
        """Log a meal entry."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        meal_date = datetime.now().strftime("%Y-%m-%d")
        
        # Get or create meal
        cursor.execute("""
            SELECT id FROM meals WHERE user_id = ? AND meal_type = ? AND meal_date = ?
        """, (user_id, meal_type, meal_date))
        
        meal = cursor.fetchone()
        if meal:
            meal_id = meal[0]
        else:
            cursor.execute("""
                INSERT INTO meals (user_id, meal_type, meal_date) VALUES (?, ?, ?)
            """, (user_id, meal_type, meal_date))
            meal_id = cursor.lastrowid
        
        # Add food entry
        cursor.execute("""
            INSERT INTO food_entries (meal_id, food_name, calories, protein, carbs, fat, serving_g, quantity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (meal_id, food_name, calories, protein, carbs, fat, serving_g, quantity))
        
        conn.commit()
        return cursor.lastrowid
    
    def add_food_to_db(self, name: str, calories: float, protein: float, 
                       carbs: float, fat: float, serving_g: float = 100) -> bool:
        """Add a custom food to the database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO food_db (name, calories, protein, carbs, fat, serving_g)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name.lower(), calories, protein, carbs, fat, serving_g))
            conn.commit()
            return True
        except Exception as e:
            _LOGGER.error("Error adding food '%s': %s", name, e)
            return False
    
    def search_food(self, query: str) -> List[Dict]:
        """Search food database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, calories, protein, carbs, fat, serving_g
            FROM food_db
            WHERE name LIKE ?
            ORDER BY name
        """, (f"%{query.lower()}%",))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user info."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_users(self) -> List[Dict]:
        """Get all users."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]
    
    def add_user(self, name: str, goal_calories: float = 2500,
                 goal_protein: float = 200, goal_carbs: float = 300,
                 goal_fat: float = 70) -> Optional[int]:
        """Add a new user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO users (name, goal_calories, goal_protein, goal_carbs, goal_fat)
                VALUES (?, ?, ?, ?, ?)
            """, (name, goal_calories, goal_protein, goal_carbs, goal_fat))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            _LOGGER.error("Error adding user '%s': %s", name, e)
            return None
    
    def set_active_user(self, user_id: int) -> bool:
        """Set active user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            return False
        
        cursor.execute("UPDATE users SET active = 1")
        cursor.execute("UPDATE users SET active = 1 WHERE id = ?", (user_id,))
        conn.commit()
        return True
    
    def get_active_user_id(self) -> int:
        """Get active user ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE active = 1 LIMIT 1")
        row = cursor.fetchone()
        return row[0] if row else 1
    
    def get_daily_totals(self) -> Dict[str, float]:
        """Get daily totals for active user."""
        user_id = self.get_active_user_id()
        today = datetime.now().strftime("%Y-%m-%d")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                SUM(fe.calories) as calories,
                SUM(fe.protein) as protein,
                SUM(fe.carbs) as carbs,
                SUM(fe.fat) as fat
            FROM food_entries fe
            JOIN meals m ON fe.meal_id = m.id
            WHERE m.user_id = ? AND m.meal_date = ?
        """, (user_id, today))
        
        row = cursor.fetchone()
        if row and row["calories"] is not None:
            return {
                "calories": round(row["calories"], 1),
                "protein": round(row["protein"], 1),
                "carbs": round(row["carbs"], 1),
                "fat": round(row["fat"], 1),
            }
        
        return {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
    
    def get_daily_meal_count(self) -> int:
        """Get number of meals today for active user."""
        user_id = self.get_active_user_id()
        today = datetime.now().strftime("%Y-%m-%d")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM meals 
            WHERE user_id = ? AND meal_date = ?
        """, (user_id, today))
        
        return cursor.fetchone()[0]
    
    def get_last_meal_time_str(self) -> Optional[str]:
        """Get last meal time as ISO string."""
        user_id = self.get_active_user_id()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT created_at FROM meals 
            WHERE user_id = ?
            ORDER BY created_at DESC LIMIT 1
        """, (user_id,))
        
        row = cursor.fetchone()
        return row[0] if row else None
    
    def get_weekly_avg_calories(self) -> float:
        """Get weekly average calories."""
        user_id = self.get_active_user_id()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        week_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        cursor.execute("""
            SELECT AVG(totals) as avg_cal
            FROM (
                SELECT SUM(fe.calories) as totals
                FROM food_entries fe
                JOIN meals m ON fe.meal_id = m.id
                WHERE m.user_id = ? AND m.meal_date >= ?
                GROUP BY m.meal_date
            )
        """, (user_id, week_start))
        
        row = cursor.fetchone()
        return round(row["avg_cal"], 1) if row and row["avg_cal"] is not None else 0
    
    def get_weekly_avg_protein(self) -> float:
        """Get weekly average protein."""
        user_id = self.get_active_user_id()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        week_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        cursor.execute("""
            SELECT AVG(totals) as avg_prot
            FROM (
                SELECT SUM(fe.protein) as totals
                FROM food_entries fe
                JOIN meals m ON fe.meal_id = m.id
                WHERE m.user_id = ? AND m.meal_date >= ?
                GROUP BY m.meal_date
            )
        """, (user_id, week_start))
        
        row = cursor.fetchone()
        return round(row["avg_prot"], 1) if row and row["avg_prot"] is not None else 0
    
    def get_recent_meals(self, limit: int = 10) -> List[Dict]:
        """Get recent meals with food entries."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT m.id, m.meal_type, m.meal_date, m.created_at,
                   fe.food_name, fe.calories, fe.protein, fe.carbs, fe.fat,
                   fe.quantity, fe.serving_g
            FROM meals m
            LEFT JOIN food_entries fe ON fe.meal_id = m.id
            WHERE m.user_id = ?
            ORDER BY m.created_at DESC
            LIMIT ?
        """, (self.get_active_user_id(), limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_goal_status(self) -> Dict:
        """Get current goal status."""
        totals = self.get_daily_totals()
        user_id = self.get_active_user_id()
        user = self.get_user_by_id(user_id)
        
        return {
            "user": user["name"] if user else "User",
            "daily": totals,
            "goals": {
                "calories": user["goal_calories"],
                "protein": user["goal_protein"],
                "carbs": user["goal_carbs"],
                "fat": user["goal_fat"],
            },
        }
    
    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
