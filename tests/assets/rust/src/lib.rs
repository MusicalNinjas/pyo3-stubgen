use pyo3::prelude::*;

/// Adds two numbers together.
///
/// Has a multi-line docstring.
#[pyfunction]
#[pyo3(name = "multiline", text_signature = "(left, right)")]
pub fn multiline(left: usize, right: usize) -> usize {
    left + right
}

/// Has a one line docstring and implicit name and signature.
#[pyfunction]
pub fn minimal(num: usize) -> usize {
    num * 2
}

#[pyfunction]
pub fn no_docstring(num: usize) -> usize {
    num - 1
}

#[pymodule]
#[pyo3(name = "testlib")]
fn py_testlib(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(multiline, module)?)?;
    module.add_function(wrap_pyfunction!(minimal, module)?)?;
    module.add_function(wrap_pyfunction!(no_docstring, module)?)?;
    Ok(())
}