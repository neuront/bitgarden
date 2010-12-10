#include <QScrollBar>
#include <QToolTip>
#include <QMouseEvent>
#include <QApplication>

struct ScrollBar
    : public QScrollBar
{
    void mousePressEvent(QMouseEvent* e)
    {
        QToolTip::showText(e->pos(), "Dragging", this, QRect(0, 0, 0, 0));
    }
};

int main(int argc, char* argv[])
{
    QApplication app(argc, argv);
    ScrollBar bar;
    bar.show();
    return app.exec();
}
