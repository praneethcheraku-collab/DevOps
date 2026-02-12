import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

class CalculatorTest {
    private Calculator calculator;

    @BeforeEach
    void setUp() {
        calculator = new Calculator();
        System.out.println("=== Starting a new test ===");
    }

    @Test
    void testAddition() {
        System.out.println("Running: 3 + 7 addition");
        assertEquals(15, calculator.add(3, 7));
        System.out.println("✓ Addition passed!\n");
    }

    @Test
    void testIsEven() {
        System.out.println("Running: Even/Odd check");
        assertTrue(calculator.isEven(4));
        assertFalse(calculator.isEven(5));
        System.out.println("✓ Even/Odd passed!\n");
    }

    @Test
    void testDivisionByZero() {
        System.out.println("Running: Division by zero");
        assertThrows(ArithmeticException.class, () -> calculator.divide(10, 0));
        System.out.println("✓ Exception test passed!\n");
    }

    @Test
    void testMultiple() {
        System.out.println("Running: Grouped assertions");
        assertAll(
            () -> assertEquals(0, calculator.add(-1, 1)),
            () -> assertEquals(5, calculator.add(2, 3)),
            () -> assertTrue(calculator.isEven(8))
        );
        System.out.println("✓ Grouped test passed!\n");
    }
}