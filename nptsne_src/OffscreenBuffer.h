#pragma once

#include <QApplication>
#include <QWindow>
#include <QOpenGLContext>
#include <QOpenGLWidget>
#include <QOffscreenSurface>
#include <QThread>
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