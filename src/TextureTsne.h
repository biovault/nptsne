#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <QApplication>
#include <QWindow>
#include <QOpenGLContext>
#include <QOpenGLWidget>
#include <QOffscreenSurface>
#include <QThread>
//#include <QOffscreenSurface>

namespace py = pybind11;

class OffscreenBuffer : public QWindow
{
public:
	OffscreenBuffer()
	{
		setSurfaceType(QWindow::OpenGLSurface);

		_context = new QOpenGLContext(this);
		_context->setFormat(requestedFormat());

		if (!_context->create())
			qFatal("Cannot create requested OpenGL context.");

		create();
	}

	QOpenGLContext* getContext() { return _context; }

	void bindContext()
	{
		_context->makeCurrent(this);
	}

	void releaseContext()
	{
		_context->doneCurrent();
	}

private:
	QOpenGLContext* _context;
};

class TextureTsne {
public:
	// constructor
	TextureTsne(
		bool verbose=false, 
		int iterations=1000, 
		int num_target_dimensions=2,
		int perplexity=30,
		int exaggeration_iter=250,
		double theta = 0.5
		);
	// tSNE transform and return results
	py::array_t<float, py::array::c_style> fit_transform(
		py::array_t<float, py::array::c_style | py::array::forcecast> X);
	
private:	
	int _num_data_points;
    int _num_dimensions;

    bool _verbose;
    int _iterations;
    int _exaggeration_iter;
    int _perplexity;
    double _theta;
    int _num_target_dimensions;
};