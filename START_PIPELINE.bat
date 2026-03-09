@echo off
REM ============================================================================
REM COMPLETE ENGLISH-ONLY NEWS INTELLIGENCE PIPELINE
REM ============================================================================

echo.
echo ================================================================================
echo    AI-DRIVEN GLOBAL NEWS KNOWLEDGE GRAPH SYSTEM
echo    WITH GUARANTEED ENGLISH-ONLY DATA COLLECTION
echo ================================================================================
echo.
echo This will run the complete pipeline:
echo.
echo   [1] Collect Latest News (English Only)
echo       - 20+ RSS feeds from BBC, CNN, Reuters, etc.
echo       - 3 API aggregators covering 230,000+ sources
echo       - AI language detection filtering
echo.
echo   [2] Process with BERT Transformer NER
echo       - Extract entities (People, Places, Organizations)
echo       - Detect 90+ relationship types
echo       - Build knowledge graph in Neo4j
echo.
echo   [3] Generate Analytics ^& Insights
echo       - Complex relationship patterns
echo       - Timeline analysis
echo       - Threat assessment
echo.
echo   [4] Launch Interactive Dashboard
echo       - Real-time knowledge graph visualization
echo       - Global threat monitoring
echo       - Entity relationship explorer
echo.
echo Language Guarantee: 100%% English data only!
echo.
echo ================================================================================
pause
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.9+ and try again.
    pause
    exit /b 1
)

REM Check if in correct directory
if not exist "run_pipeline.py" (
    echo ERROR: run_pipeline.py not found!
    echo Make sure you're running this from the transformer directory.
    pause
    exit /b 1
)

echo Starting English-Only Pipeline...
echo.

REM Run the complete pipeline
python run_pipeline.py

echo.
echo ================================================================================
echo Pipeline Execution Complete!
echo ================================================================================
echo.
echo Quick Commands:
echo   - Launch Dashboard:  streamlit run dashboard.py
echo   - Neo4j Browser:     start http://localhost:7474
echo   - Verify English:    python verify_english_only.py
echo   - Check Data Age:    python check_data_freshness.py
echo.
echo ================================================================================
pause
