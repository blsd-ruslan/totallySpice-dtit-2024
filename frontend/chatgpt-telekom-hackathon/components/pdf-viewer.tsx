'use client'

import {Card, CardContent} from "@/components/ui/card"
import {useState} from "react"

interface PDFViewerProps {
    pdfUrl: string
    title?: string
}

export default function PDFViewer({pdfUrl, title = "Document Viewer"}: PDFViewerProps) {
    const [isLoading, setIsLoading] = useState(true)

    const pdfData = {
        "field_name": "valid until",
        "field_value": "01.01.1900",
        "reason": "The date \"01.01.1900\" is likely too far in the past to be a valid \"valid until\" date, which typically refers to a future date.",
        "coordinates": {
            "x0": 36.84000015258789,
            "y0": 673.8800048828125,
            "x1": 161.63999938964844,
            "y1": 732.4400024414062
        },
        "page_number": 1
    };

    return (
        <Card className="w-full max-w-7xl border-2 border-solid rounded-2xl mx-auto max-h-[700px]">
            <CardContent className="p-1 sm:p-2 h-full">
                <div className="relative size-full rounded-lg overflow-hidden bg-muted">
                    {/*{isLoading && (*/}
                    {/*    <div className="absolute inset-0 flex items-center justify-center bg-background/80">*/}
                    {/*        <Loader2 className="size-8 animate-spin"/>*/}
                    {/*    </div>*/}
                    {/*)}*/}
                    <iframe
                        src={`${pdfUrl}#page=1&zoom=100,161,732`}
                        className="size-full border-0"
                        onLoad={() => setIsLoading(false)}
                        title={title}
                    />
                </div>
            </CardContent>
        </Card>
    )
}

