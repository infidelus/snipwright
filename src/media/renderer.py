from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QImage,
    QPixmap,
)


def render_frame(
        frame,
        container,
        width=None,
        height=None,
        fast=False,
):

    img = frame.to_ndarray(
        format="rgb24"
    )

    h, w, c = img.shape

    qimg = QImage(
        img.data,
        w,
        h,
        w * c,
        QImage.Format_RGB888
    )

    pix = QPixmap.fromImage(
        qimg
    )

    #
    # Correct DAR
    #

    try:

        stream = (
            container
            .streams
            .video[0]
        )

        dar = (
            stream
            .display_aspect_ratio
        )

        if dar:

            corrected_width = int(
                h
                *
                float(
                    dar
                )
            )

            pix = pix.scaled(

                corrected_width,

                h,

                Qt.IgnoreAspectRatio,

                Qt.FastTransformation if fast else Qt.SmoothTransformation

            )

    except Exception:

        pass

    if width:

        pix = pix.scaled(

            width,

            height,

            Qt.KeepAspectRatio,

            Qt.SmoothTransformation,

        )

    return pix

def capture_image(frame, container, deinterlace=False):
    """A frame as a full-size QImage for Capture Frame, corrected to the
    display shape as render_frame() corrects the preview.

    `deinterlace` runs it through yadif first when the frame is flagged
    interlaced - a still of broadcast motion is otherwise combed.  One frame
    is enough: yadif then interpolates from the frame's own fields, which is
    what a still needs.  A progressive frame is left exactly as decoded.
    """
    if deinterlace and getattr(frame, "interlaced_frame", False):
        try:
            import av.filter
            graph = av.filter.Graph()
            src = graph.add_buffer(template=container.streams.video[0])
            yadif = graph.add("yadif", "mode=0:deint=interlaced")
            sink = graph.add("buffersink")
            src.link_to(yadif)
            yadif.link_to(sink)
            graph.configure()
            graph.push(frame)
            graph.push(None)
            frame = graph.pull()
        except Exception:
            pass        # an undeinterlaced picture beats no picture
    return render_frame(frame, container).toImage()
