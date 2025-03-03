import functools
import time
import hashlib
import pickle
import os
import threading
import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, TypeVar, cast

# Variables de type pour une meilleure indication de type
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

class CacheRegistry:
    """
    Registre pour suivre toutes les fonctions mises en cache et leurs statistiques.
    Utile pour surveiller et vider les caches.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CacheRegistry, cls).__new__(cls)
                cls._instance._caches = {}
                cls._instance._stats = {}
            return cls._instance
    
    def register(self, func_name: str, cache_obj: Dict, cache_type: str) -> None:
        """Enregistre un objet cache dans le registre"""
        self._caches[func_name] = {
            'cache': cache_obj,
            'type': cache_type,
            'created_at': datetime.datetime.now()
        }
        self._stats[func_name] = {
            'hits': 0,
            'misses': 0,
            'total_time_saved': 0.0
        }
    
    def update_stats(self, func_name: str, hit: bool, time_saved: float = 0.0) -> None:
        """Met à jour les statistiques du cache"""
        if func_name in self._stats:
            if hit:
                self._stats[func_name]['hits'] += 1
                self._stats[func_name]['total_time_saved'] += time_saved
            else:
                self._stats[func_name]['misses'] += 1
    
    def clear_cache(self, func_name: Optional[str] = None) -> None:
        """Vide un cache spécifique ou tous les caches"""
        if func_name is not None and func_name in self._caches:
            self._caches[func_name]['cache'].clear()
            self._stats[func_name] = {'hits': 0, 'misses': 0, 'total_time_saved': 0.0}
        elif func_name is None:
            for cache_info in self._caches.values():
                cache_info['cache'].clear()
            for func_name in self._stats:
                self._stats[func_name] = {'hits': 0, 'misses': 0, 'total_time_saved': 0.0}
    
    def get_stats(self, func_name: Optional[str] = None) -> Dict:
        """Obtient les statistiques pour une fonction spécifique ou toutes les fonctions"""
        if func_name is not None:
            return self._stats.get(func_name, {})
        return {
            'per_function': self._stats,
            'summary': {
                'total_functions': len(self._stats),
                'total_hits': sum(stats['hits'] for stats in self._stats.values()),
                'total_misses': sum(stats['misses'] for stats in self._stats.values()),
                'total_time_saved': sum(stats['total_time_saved'] for stats in self._stats.values()),
            }
        }
    
    def get_cache_info(self) -> Dict:
        """Obtient des informations sur tous les caches enregistrés"""
        return {
            func_name: {
                'type': info['type'],
                'size': len(info['cache']),
                'created_at': info['created_at']
            }
            for func_name, info in self._caches.items()
        }

# Initialisation du registre
cache_registry = CacheRegistry()

def memoize(func: F) -> F:
    """
    Décorateur de mise en cache en mémoire de base.
    Met en cache les résultats en fonction des arguments de la fonction.
    
    Args:
        func: La fonction à mettre en cache
        
    Returns:
        Fonction décorée avec mise en cache
    """
    cache: Dict[str, Any] = {}
    cache_registry.register(func.__name__, cache, 'memoize')
    
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Création d'une clé à partir des arguments de la fonction
        key_parts = [repr(arg) for arg in args]
        key_parts.extend(f"{k}={repr(v)}" for k, v in sorted(kwargs.items()))
        key = ":".join(key_parts)
        
        # Vérification si le résultat est dans le cache
        if key in cache:
            cache_registry.update_stats(func.__name__, hit=True)
            return cache[key]
        
        # Calcul du résultat et stockage dans le cache
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        cache[key] = result
        cache_registry.update_stats(func.__name__, hit=False)
        
        return result
    
    return cast(F, wrapper)

def timed_cache(seconds: int = 300) -> Callable[[F], F]:
    """
    Décorateur de mise en cache basé sur le temps.
    Met en cache les résultats pendant un nombre spécifié de secondes.
    
    Args:
        seconds: Nombre de secondes pendant lesquelles mettre en cache les résultats
        
    Returns:
        Fonction décorateur
    """
    def decorator(func: F) -> F:
        cache: Dict[str, Tuple[Any, float]] = {}
        cache_registry.register(func.__name__, cache, f'timed_cache({seconds}s)')
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Création d'une clé à partir des arguments de la fonction
            key_parts = [repr(arg) for arg in args]
            key_parts.extend(f"{k}={repr(v)}" for k, v in sorted(kwargs.items()))
            key = ":".join(key_parts)
            
            current_time = time.time()
            
            # Vérification si le résultat est dans le cache et n'est pas expiré
            if key in cache:
                result, timestamp = cache[key]
                if current_time - timestamp < seconds:
                    # Calcul du temps économisé
                    start_time = time.time()
                    _ = func(*args, **kwargs)  # Exécution mais sans utiliser le résultat
                    time_saved = time.time() - start_time
                    
                    cache_registry.update_stats(func.__name__, hit=True, time_saved=time_saved)
                    return result
            
            # Calcul du résultat et stockage dans le cache
            result = func(*args, **kwargs)
            cache[key] = (result, current_time)
            cache_registry.update_stats(func.__name__, hit=False)
            
            return result
        
        return cast(F, wrapper)
    
    return decorator

def lru_cache(maxsize: int = 128) -> Callable[[F], F]:
    """
    Décorateur de cache Least Recently Used (LRU).
    Limite la taille du cache en supprimant les éléments les moins récemment utilisés.
    
    Args:
        maxsize: Nombre maximum d'éléments à stocker dans le cache
        
    Returns:
        Fonction décorateur
    """
    def decorator(func: F) -> F:
        # Utilisation d'OrderedDict pour suivre l'ordre d'utilisation
        cache: Dict[str, Any] = {}
        usage_order: List[str] = []
        cache_registry.register(func.__name__, cache, f'lru_cache(maxsize={maxsize})')
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Création d'une clé à partir des arguments de la fonction
            key_parts = [repr(arg) for arg in args]
            key_parts.extend(f"{k}={repr(v)}" for k, v in sorted(kwargs.items()))
            key = ":".join(key_parts)
            
            # Vérification si le résultat est dans le cache
            if key in cache:
                # Mise à jour de l'ordre d'utilisation
                usage_order.remove(key)
                usage_order.append(key)
                
                cache_registry.update_stats(func.__name__, hit=True)
                return cache[key]
            
            # Calcul du résultat
            result = func(*args, **kwargs)
            
            # Ajout au cache
            cache[key] = result
            usage_order.append(key)
            
            # Suppression de l'élément le plus ancien si le cache est plein
            if len(cache) > maxsize:
                oldest_key = usage_order.pop(0)
                del cache[oldest_key]
            
            cache_registry.update_stats(func.__name__, hit=False)
            return result
        
        return cast(F, wrapper)
    
    return decorator

def disk_cache(directory: str = '.cache', expiration: Optional[int] = None) -> Callable[[F], F]:
    """
    Décorateur de mise en cache sur disque.
    Stocke les résultats sur disque pour la persistance entre les exécutions du programme.
    
    Args:
        directory: Répertoire pour stocker les fichiers de cache
        expiration: Temps d'expiration optionnel en secondes
        
    Returns:
        Fonction décorateur
    """
    # Création du répertoire de cache s'il n'existe pas
    os.makedirs(directory, exist_ok=True)
    
    def decorator(func: F) -> F:
        # Suivi des fichiers de cache en mémoire
        cache_files: Dict[str, str] = {}
        cache_registry.register(func.__name__, cache_files, f'disk_cache(dir={directory})')
        
        def create_cache_key(args: Any, kwargs: Any) -> Tuple[str, str]:
            """Crée une clé de cache et le chemin du fichier correspondant"""
            key_parts = [repr(arg) for arg in args]
            key_parts.extend(f"{k}={repr(v)}" for k, v in sorted(kwargs.items()))
            key_str = ":".join(key_parts)
            
            key_hash = hashlib.md5(key_str.encode()).hexdigest()
            cache_file = os.path.join(directory, f"{func.__name__}_{key_hash}.cache")
            cache_files[key_str] = cache_file
            
            return key_str, cache_file
        
        def get_from_cache(cache_file: str) -> Optional[Any]:
            """Tente de récupérer un résultat du cache"""
            if not os.path.exists(cache_file):
                return None
                
            file_age = time.time() - os.path.getmtime(cache_file)
            if expiration is not None and file_age >= expiration:
                return None
                
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except (pickle.PickleError, EOFError):
                return None
        
        def save_to_cache(cache_file: str, result: Any) -> None:
            """Sauvegarde un résultat dans le cache"""
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump(result, f)
            except (pickle.PickleError, IOError):
                pass  # Ignorer les erreurs d'écriture
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key_str, cache_file = create_cache_key(args, kwargs)
            
            # Essayer de récupérer du cache
            cached_result = get_from_cache(cache_file)
            if cached_result is not None:
                cache_registry.update_stats(func.__name__, hit=True)
                return cached_result
            
            # Calculer le résultat
            result = func(*args, **kwargs)
            
            # Sauvegarder dans le cache
            save_to_cache(cache_file, result)
            cache_registry.update_stats(func.__name__, hit=False)
            
            return result
        
        return cast(F, wrapper)
    
    return decorator

def parametrized_cache(param_name: str) -> Callable[[F], F]:
    """
    Décorateur de mise en cache paramétré.
    Permet d'activer/désactiver le cache en fonction d'un paramètre.
    
    Args:
        param_name: Nom du paramètre qui contrôle la mise en cache
        
    Returns:
        Fonction décorateur
    """
    def decorator(func: F) -> F:
        cache: Dict[str, Any] = {}
        cache_registry.register(func.__name__, cache, f'parametrized_cache(param={param_name})')
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Vérification si la mise en cache est activée pour cet appel
            use_cache = kwargs.pop(param_name, True)
            
            if not use_cache:
                # Ignorer le cache s'il est désactivé
                return func(*args, **kwargs)
            
            # Création d'une clé à partir des arguments de la fonction
            key_parts = [repr(arg) for arg in args]
            key_parts.extend(f"{k}={repr(v)}" for k, v in sorted(kwargs.items()))
            key = ":".join(key_parts)
            
            # Vérification si le résultat est dans le cache
            if key in cache:
                cache_registry.update_stats(func.__name__, hit=True)
                return cache[key]
            
            # Calcul du résultat et stockage dans le cache
            result = func(*args, **kwargs)
            cache[key] = result
            cache_registry.update_stats(func.__name__, hit=False)
            
            return result
        
        return cast(F, wrapper)
    
    return decorator

def clear_all_caches() -> None:
    """Vide tous les caches enregistrés"""
    cache_registry.clear_cache()

def clear_cache_for_function(func_name: str) -> None:
    """Vide le cache pour une fonction spécifique"""
    cache_registry.clear_cache(func_name)

def get_cache_stats(func_name: Optional[str] = None) -> Dict:
    """Obtient les statistiques du cache"""
    return cache_registry.get_stats(func_name)

def get_cache_info() -> Dict:
    """Obtient des informations sur tous les caches enregistrés"""
    return cache_registry.get_cache_info()

# Exemple d'utilisation
if __name__ == "__main__":
    # Exemple avec mémoïsation de base
    @memoize
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)
    
    # Exemple avec cache temporisé
    @timed_cache(seconds=10)
    def fetch_data(url):
        print(f"Récupération des données depuis {url}...")
        time.sleep(1)  # Simulation d'une requête réseau
        return f"Données de {url}"
    
    # Exemple avec cache LRU
    @lru_cache(maxsize=2)
    def get_user(user_id):
        print(f"Récupération de l'utilisateur {user_id}...")
        time.sleep(0.5)  # Simulation d'une requête de base de données
        return f"Utilisateur {user_id}"
    
    # Exemple avec cache sur disque
    @disk_cache(directory='.cache', expiration=3600)
    def process_large_data(data_id):
        print(f"Traitement des données volumineuses {data_id}...")
        time.sleep(2)  # Simulation d'un calcul lourd
        return f"Données traitées {data_id}"
    
    # Exemple avec cache paramétré
    @parametrized_cache(param_name='use_cache')
    def get_weather(city):
        print(f"Récupération de la météo pour {city}...")
        time.sleep(0.5)  # Simulation d'un appel API
        return f"Météo pour {city}: Ensoleillé"
    
    # Exécution des exemples
    print("Test des décorateurs de mise en cache...")
    
    # Test fibonacci
    print("\nExemple de Fibonacci:")
    print(fibonacci(10))  # Va calculer
    print(fibonacci(10))  # Va utiliser le cache
    
    # Test fetch_data
    print("\nExemple de récupération de données:")
    print(fetch_data("https://example.com"))  # Va récupérer
    print(fetch_data("https://example.com"))  # Va utiliser le cache
    
    # Test get_user avec LRU
    print("\nExemple de cache LRU:")
    print(get_user(1))  # Va interroger
    print(get_user(2))  # Va interroger
    print(get_user(3))  # Va interroger, évincer l'utilisateur 1
    print(get_user(1))  # Va interroger à nouveau (a été évincé)
    print(get_user(2))  # Va utiliser le cache
    
    # Test disk_cache
    print("\nExemple de cache sur disque:")
    print(process_large_data("dataset1"))  # Va traiter
    print(process_large_data("dataset1"))  # Va utiliser le cache
    
    # Test parametrized_cache
    print("\nExemple de cache paramétré:")
    print(get_weather("New York"))  # Va récupérer
    print(get_weather("New York"))  # Va utiliser le cache
    print(get_weather("New York", use_cache=False))  # Va récupérer à nouveau
    
    # Affichage des statistiques
    print("\nStatistiques du cache:")
    print(get_cache_stats()) 