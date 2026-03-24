// mnheme/kotlin/android/MnhemeViewModel.kt
// ==========================================
// Example Android ViewModel using MemoryDB with Coroutines.
// This shows how to integrate mnheme into an Android app with:
//   - LiveData for UI observation
//   - Dispatchers.IO for all DB work (never block main thread)
//   - StateFlow for reactive UI

package com.example.mnheme.android

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import mnheme.Feeling
import mnheme.MemoryDB
import mnheme.Memory

class MnhemeViewModel(application: Application) : AndroidViewModel(application) {

    // DB lives on IO dispatcher — file is in app's private files dir
    private val db: MemoryDB by lazy {
        MemoryDB(application.filesDir.resolve("mente.mnheme"))
    }

    // ── State ─────────────────────────────────────────────────────

    private val _memories  = MutableStateFlow<List<Memory>>(emptyList())
    val memories: StateFlow<List<Memory>> = _memories

    private val _concepts  = MutableStateFlow<List<String>>(emptyList())
    val concepts: StateFlow<List<String>> = _concepts

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    private val _error     = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    // ── Commands ──────────────────────────────────────────────────

    fun remember(concept: String, feeling: Feeling, content: String, note: String = "") {
        viewModelScope.launch {
            _isLoading.value = true
            runCatching {
                withContext(Dispatchers.IO) {
                    db.remember(concept, feeling, content, note)
                }
            }.onSuccess {
                loadAll()  // refresh
            }.onFailure {
                _error.postValue(it.message)
            }
            _isLoading.value = false
        }
    }

    fun recall(concept: String, feeling: Feeling? = null) {
        viewModelScope.launch {
            _isLoading.value = true
            runCatching {
                withContext(Dispatchers.IO) {
                    db.recall(concept, feeling)
                }
            }.onSuccess { _memories.value = it }
             .onFailure { _error.postValue(it.message) }
            _isLoading.value = false
        }
    }

    fun loadAll() {
        viewModelScope.launch {
            withContext(Dispatchers.IO) {
                _memories.value = db.recallAll()
                _concepts.value = db.listConcepts()
            }
        }
    }

    fun search(query: String) {
        viewModelScope.launch {
            val results = withContext(Dispatchers.IO) { db.search(query) }
            _memories.value = results
        }
    }

    fun feelingDistribution(): Map<String, Int> = db.feelingDistribution()

    fun count(): Int = db.count()

    override fun onCleared() {
        super.onCleared()
        db.close()
    }
}

// ── build.gradle.kts (app module) ────────────────────────────────
//
// dependencies {
//     // Kotlin coroutines
//     implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.0")
//     // ViewModel + LiveData
//     implementation("androidx.lifecycle:lifecycle-viewmodel-ktx:2.8.0")
//     implementation("androidx.lifecycle:lifecycle-livedata-ktx:2.8.0")
//     // org.json is already available on Android (no extra dep needed)
// }
