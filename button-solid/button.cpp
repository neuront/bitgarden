#include <QApplication>
#include <QToolButton>
#include <QBrush>
#include <QLinearGradient>
#include <QPainter>

struct SolidButton
    : public QToolButton
{
    SolidButton()
    {
        setFixedSize(128, 128);
    }

    void paintEvent(QPaintEvent*)
    {
        isDown() ? paint(QColor(0xe8, 0xf0, 0xf8), QColor(0xf0, 0xf0, 0xf8))
                 : paint(QColor(0xff, 0xff, 0xff), QColor(0xcc, 0xdd, 0xf0));
        paintBorder();
    }

    void paint(QColor topColor, QColor bottomColor)
    {
        QLinearGradient grad(rect().topLeft(), rect().bottomLeft());
        grad.setSpread(QGradient::PadSpread);
        grad.setColorAt(0, topColor);
        grad.setColorAt(1, bottomColor);
        QBrush brush(grad);

        QPainter painter(this);
        painter.fillRect(rect(), brush);
    }

    void paintBorder()
    {
        QPainter painter(this);
        painter.setBrush(Qt::NoBrush);
        painter.setPen(QPen(QColor(0xa8, 0xb0, 0xb8), 3));
        painter.drawRect(rect().adjusted(1, 1, -2, -2));
        painter.setPen(QPen(QColor(0xff, 0xff, 0xff, 0x5f), 3));
        painter.drawRect(rect().adjusted(4, 4, -5, -5));
    }

};

int main(int argc, char* argv[])
{
    QApplication app(argc, argv);
    SolidButton button;
    button.show();
    return app.exec();
}
