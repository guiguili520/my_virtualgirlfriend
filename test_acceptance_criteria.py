#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Acceptance Criteria Test Suite
Tests all requirements from the ticket
"""

from scenarios import (
    SCENARIO_CATALOG,
    validate_catalog,
    get_catalog_metadata,
    get_scenario_by_name,
    get_scenarios_by_category,
    get_scenarios_by_tag
)
from generator import GirlfriendDatasetGenerator


def test_scenario_count():
    """Test: At least 50 distinct dialogue scenarios"""
    print("\n" + "="*60)
    print("TEST 1: Scenario Count (≥50 required)")
    print("="*60)
    
    count = len(SCENARIO_CATALOG)
    print(f"Total scenarios: {count}")
    assert count >= 50, f"Expected ≥50 scenarios, got {count}"
    print("✅ PASS - 50+ scenarios requirement met")
    return True


def test_unique_instructions():
    """Test: Unique instruction strings for each scenario"""
    print("\n" + "="*60)
    print("TEST 2: Unique Instruction Strings")
    print("="*60)
    
    instructions = [s.instruction for s in SCENARIO_CATALOG]
    unique_instructions = set(instructions)
    
    print(f"Total instructions: {len(instructions)}")
    print(f"Unique instructions: {len(unique_instructions)}")
    
    assert len(instructions) == len(unique_instructions), "Instructions are not unique"
    print("✅ PASS - All instruction strings are unique")
    return True


def test_scenario_structure():
    """Test: Each scenario has proper structure"""
    print("\n" + "="*60)
    print("TEST 3: Scenario Structure Validation")
    print("="*60)
    
    for scenario in SCENARIO_CATALOG:
        # Check required fields
        assert scenario.name, "Scenario missing name"
        assert scenario.instruction, "Scenario missing instruction"
        assert scenario.response_templates, "Scenario missing response templates"
        assert len(scenario.response_templates) > 0, "Scenario needs at least one response"
        assert scenario.category, "Scenario missing category"
        assert scenario.tags, "Scenario missing tags"
        
        # Check persona consistency in responses
        for response in scenario.response_templates:
            assert response.strip(), "Response template cannot be empty"
    
    print(f"Validated {len(SCENARIO_CATALOG)} scenarios")
    print("✅ PASS - All scenarios have proper structure")
    return True


def test_taxonomy_coverage():
    """Test: Taxonomy covers required categories"""
    print("\n" + "="*60)
    print("TEST 4: Taxonomy Coverage")
    print("="*60)
    
    metadata = get_catalog_metadata()
    categories = metadata['categories']
    
    required_categories = [
        'greetings', 'emotional_care', 'life_care', 'hobbies',
        'festivals', 'conflict_resolution', 'future_planning'
    ]
    
    print(f"Total categories: {len(categories)}")
    print(f"Required categories: {required_categories}")
    
    for cat in required_categories:
        assert cat in categories, f"Missing required category: {cat}"
        print(f"  ✓ {cat}")
    
    print("✅ PASS - All required categories present")
    return True


def test_metadata_access():
    """Test: Metadata is programmatically accessible"""
    print("\n" + "="*60)
    print("TEST 5: Programmatic Metadata Access")
    print("="*60)
    
    # Test get_catalog_metadata
    metadata = get_catalog_metadata()
    assert 'total_scenarios' in metadata
    assert 'categories' in metadata
    assert 'tags' in metadata
    assert 'scenario_names' in metadata
    print("  ✓ get_catalog_metadata() works")
    
    # Test get_scenario_by_name
    scenario = get_scenario_by_name("morning_greeting")
    assert scenario is not None
    assert scenario.name == "morning_greeting"
    print("  ✓ get_scenario_by_name() works")
    
    # Test get_scenarios_by_category
    greetings = get_scenarios_by_category("greetings")
    assert len(greetings) > 0
    print(f"  ✓ get_scenarios_by_category() works ({len(greetings)} greeting scenarios)")
    
    # Test get_scenarios_by_tag
    love_scenarios = get_scenarios_by_tag("love")
    assert len(love_scenarios) > 0
    print(f"  ✓ get_scenarios_by_tag() works ({len(love_scenarios)} love scenarios)")
    
    print("✅ PASS - All metadata access functions work")
    return True


def test_deterministic_enumeration():
    """Test: Can enumerate scenarios deterministically"""
    print("\n" + "="*60)
    print("TEST 6: Deterministic Enumeration")
    print("="*60)
    
    generator = GirlfriendDatasetGenerator()
    
    # Generate dataset deterministically (each scenario once)
    dataset = generator.generate_deterministic_dataset(variations_per_scenario=1)
    
    print(f"Generated samples: {len(dataset)}")
    print(f"Expected samples: {len(SCENARIO_CATALOG)}")
    
    assert len(dataset) == len(SCENARIO_CATALOG), "Deterministic generation failed"
    
    # Verify each instruction appears exactly once
    instructions = [entry['instruction'] for entry in dataset]
    unique_instructions = set(instructions)
    
    assert len(instructions) == len(unique_instructions), "Instructions not unique in dataset"
    print("✅ PASS - Deterministic enumeration works correctly")
    return True


def test_persona_consistency():
    """Test: Persona attributes in seed templates"""
    print("\n" + "="*60)
    print("TEST 7: Persona Consistency")
    print("="*60)
    
    # Count responses with emoji
    total_responses = 0
    responses_with_emoji = 0
    
    for scenario in SCENARIO_CATALOG:
        for response in scenario.response_templates:
            total_responses += 1
            # Check for emoji (Unicode characters > 0x1F000)
            if any(ord(char) > 0x1F000 for char in response):
                responses_with_emoji += 1
    
    emoji_percentage = (responses_with_emoji / total_responses) * 100
    
    print(f"Total response templates: {total_responses}")
    print(f"Responses with emoji: {responses_with_emoji}")
    print(f"Emoji coverage: {emoji_percentage:.2f}%")
    
    # Check for tone words (语气词)
    tone_words = ['呀', '啦', '哦', '呢', '嘛', '~', '！']
    responses_with_tone = 0
    
    for scenario in SCENARIO_CATALOG:
        for response in scenario.response_templates:
            if any(word in response for word in tone_words):
                responses_with_tone += 1
    
    tone_percentage = (responses_with_tone / total_responses) * 100
    print(f"Responses with tone words: {responses_with_tone}")
    print(f"Tone word coverage: {tone_percentage:.2f}%")
    
    # We expect high emoji and tone word coverage (>75% for templates is good)
    assert emoji_percentage > 75, f"Low emoji coverage: {emoji_percentage}%"
    assert tone_percentage > 75, f"Low tone word coverage: {tone_percentage}%"
    
    print("✅ PASS - Persona consistency maintained")
    return True


def test_validation_mechanism():
    """Test: Built-in validation guarantees catalog quality"""
    print("\n" + "="*60)
    print("TEST 8: Validation Mechanism")
    print("="*60)
    
    try:
        validate_catalog()
        print("✅ PASS - Validation mechanism works")
        return True
    except AssertionError as e:
        print(f"❌ FAIL - Validation failed: {e}")
        return False


def test_modular_architecture():
    """Test: Code is properly modularized"""
    print("\n" + "="*60)
    print("TEST 9: Modular Architecture")
    print("="*60)
    
    # Check that modules can be imported separately
    try:
        import scenarios
        import generator
        print("  ✓ scenarios.py module exists and is importable")
        print("  ✓ generator.py module exists and is importable")
        
        # Check key components exist
        assert hasattr(scenarios, 'Scenario'), "Scenario class missing"
        assert hasattr(scenarios, 'SCENARIO_CATALOG'), "SCENARIO_CATALOG missing"
        assert hasattr(generator, 'GirlfriendDatasetGenerator'), "Generator class missing"
        print("  ✓ Key components are accessible")
        
        print("✅ PASS - Modular architecture verified")
        return True
    except ImportError as e:
        print(f"❌ FAIL - Module import failed: {e}")
        return False


def run_all_tests():
    """Run all acceptance criteria tests"""
    print("\n" + "="*70)
    print(" " * 15 + "ACCEPTANCE CRITERIA TEST SUITE")
    print("="*70)
    
    tests = [
        test_scenario_count,
        test_unique_instructions,
        test_scenario_structure,
        test_taxonomy_coverage,
        test_metadata_access,
        test_deterministic_enumeration,
        test_persona_consistency,
        test_validation_mechanism,
        test_modular_architecture
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append((test_func.__name__, result))
        except Exception as e:
            print(f"\n❌ EXCEPTION in {test_func.__name__}: {e}")
            results.append((test_func.__name__, False))
    
    # Summary
    print("\n" + "="*70)
    print(" " * 25 + "TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL ACCEPTANCE CRITERIA MET! 🎉")
        print("="*70)
        return True
    else:
        print("\n⚠️  Some tests failed")
        print("="*70)
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
