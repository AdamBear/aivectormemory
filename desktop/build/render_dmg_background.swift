import AppKit
import Foundation

guard CommandLine.arguments.count >= 3 else {
    fputs("Usage: render_dmg_background.swift <background> <output>\n", stderr)
    exit(1)
}

let backgroundPath = CommandLine.arguments[1]
let outputPath = CommandLine.arguments[2]

guard let background = NSImage(contentsOfFile: backgroundPath) else {
    fputs("Failed to load background image: \(backgroundPath)\n", stderr)
    exit(1)
}

let size = background.size
let outputImage = NSImage(size: size)

outputImage.lockFocus()
background.draw(in: NSRect(origin: .zero, size: size), from: .zero, operation: .copy, fraction: 1.0)
NSColor(calibratedWhite: 1.0, alpha: 0.60).setFill()
NSBezierPath(rect: NSRect(origin: .zero, size: size)).fill()
outputImage.unlockFocus()

guard
    let tiffData = outputImage.tiffRepresentation,
    let bitmap = NSBitmapImageRep(data: tiffData),
    let pngData = bitmap.representation(using: .png, properties: [:])
else {
    fputs("Failed to render output image.\n", stderr)
    exit(1)
}

let outputURL = URL(fileURLWithPath: outputPath)
try FileManager.default.createDirectory(at: outputURL.deletingLastPathComponent(), withIntermediateDirectories: true, attributes: nil)
try pngData.write(to: outputURL)
