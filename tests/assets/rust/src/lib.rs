use pyo3::prelude::*;

/// Adds two numbers together
///
/// Has a multi-line docstring
#[pyfunction]
#[pyo3(name = "add", text_signature = "(left, right)")]
pub fn add(left: usize, right: usize) -> usize {
    left + right
}

/// Has a one line docstring and one argument
#[pyfunction]
#[pyo3(name = "double", text_signature = "(num)")]
pub fn double(num: usize) -> usize {
    num * 2
}

#[pyfunction]
#[pyo3(name = "no_docstring", text_signature = "(num)")]
pub fn decrement(num: usize) -> usize {
    num - 1
}

/// A docstring but no signature
#[pyfunction]
pub fn no_signature(num: usize) -> usize {
    num * 2
}

#[pyfunction]
#[pyo3(name = "neither")]
pub fn subtract(left: usize, right: usize) -> usize {
    left - right
}

#[pymodule]
#[pyo3(name = "testlib")]
fn py_testlib(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(add, module)?)?;
    module.add_function(wrap_pyfunction!(double, module)?)?;
    module.add_function(wrap_pyfunction!(decrement, module)?)?;
    module.add_function(wrap_pyfunction!(no_signature, module)?)?;
    module.add_function(wrap_pyfunction!(subtract, module)?)?;
    Ok(())
}